#include "sbpy.h"
#include "stats.h"
#include "pk_dealer.h"

#ifdef WIN32
	#include "windows.h"
	#include <time.h>
#else
	#include <sys/time.h>
#endif

#include <cstddef>
#include <vector>
#include <map>
#include <utility>
#include <string>

namespace stats
{
	// Gets the current number of microseconds since the epoch
	bigint get_epoch_micros()
	{
		// Based on code found at the following page
		// http://brian.pontarelli.com/2009/01/05/getting-the-current-system-time-in-milliseconds-with-c/
		// I don't know how to get microseconds on Windows. May not even be possible.
		#ifdef WIN32
			// For Windows
			SYSTEMTIME stime;
			GetSystemTime(&stime);
			bigint seconds = time();
			bigint milliseconds = stime.wMilliseconds;
			bigint total = (seconds * 1000000) + (milliseconds * 1000);
		#else
			// For Linux/Unix/OSX
			timeval time;
			gettimeofday(&time, NULL);
			bigint seconds = time.tv_sec;
			bigint microseconds = time.tv_usec;
			bigint total = (seconds * 1000000) + microseconds;
		#endif
		return total;
	}

	// Primary storage

	match *current_match;
	std::vector<activity_span*> activity_spans;
	std::vector<capture_event*> capture_events;
	std::vector<damage_dealt_event*> damage_dealt_events;
	std::vector<death_event*> death_events;
	std::vector<frag_event*> frag_events;
	std::vector<shot_event*> shot_events;

	// Primary key dealers

	pk_dealer *matches_pk_dealer 				= new pk_dealer(1);
	pk_dealer *activity_spans_pk_dealer			= new pk_dealer(150);
	pk_dealer *capture_events_pk_dealer 		= new pk_dealer(100);
	pk_dealer *damage_dealt_events_pk_dealer 	= new pk_dealer(1000);
	pk_dealer *death_events_pk_dealer 			= new pk_dealer(600);
	pk_dealer *frag_events_pk_dealer 			= new pk_dealer(800);
	pk_dealer *shot_events_pk_dealer 			= new pk_dealer(1500);
	
	struct pk_dealer_entry
	{
		pk_dealer* pkd;
		const char *name;
	};
	
	pk_dealer_entry pk_dealers[] = {
			{matches_pk_dealer, "matches_pks"},
			{activity_spans_pk_dealer, "activity_spans_pks"},
			{capture_events_pk_dealer, "capture_events_pks"},
			{damage_dealt_events_pk_dealer, "damage_dealt_events_pks"},
			{death_events_pk_dealer, "death_events_pks"},
			{frag_events_pk_dealer, "frag_events_pks"},
			{shot_events_pk_dealer, "shot_events_pks"}
	};
	#define pk_dealers_count sizeof(pk_dealers)/sizeof(pk_dealer_entry)

	// Staging storage

	std::map<bigint/*user_id*/, activity_span*> current_activity_spans;
	std::map<std::pair<bigint, int>, shot_event*> pending_shots;
	std::map<std::pair<bigint, short>, capture_event*> pending_captures;

	// Private stuff

	static PyObject *appropriate_pks_callback(PyObject *pk_dealer, PyObject *args)
	{
		int pk_dealer_index; 
		bigint cur; 
		bigint end;
		if(!PyArg_ParseTuple(args, "iLL", &pk_dealer_index, &cur, &end))
			return 0;
		
		pk_dealers[pk_dealer_index].pkd->add_counter(cur, end);
		
		Py_INCREF(Py_None);
		return Py_None;
	}

	PyMethodDef appropriate_pks_callback_method_def = {"appropriate_pks_callback", appropriate_pks_callback, METH_VARARGS, "Stats primary key appropriation callback."};

	void appropriate_pks()
	{
		for(unsigned int i=0; i < pk_dealers_count; i++)
		{
			bigint order = pk_dealers[i].pkd->order_pks();
			if(order)
			{
				PyObject *appropriate_pks_callback_pymethod = PyCFunction_New(&appropriate_pks_callback_method_def, NULL);
				SbPy::triggerEventf("data_request", "spiq", pk_dealers[i].name, appropriate_pks_callback_pymethod, i, order);
			}
		}
	}
	
	#include "dump_stats.cpp"

	// Public methods

	void initialize()
	{
		// Appropriate initial batch of stats PKs
		appropriate_pks();
		current_match = NULL;
	}

	void update()
	{
		// Issue additional stats PK appropriations when available numbers get low
		appropriate_pks();
	}

	void start_match(short mode_id, char *map_name, short pseudomode_id, int instance_id)
	{
		// Get the match pk and bail if one isn't given
		bigint pk = matches_pk_dealer->deal();
		if(pk < 0) return;

		current_match = new match;
		current_match->id = pk;
		strncpy((char *)&current_match->map_name, map_name, 33);
		current_match->map_name[33] = '\0';
		current_match->mode_id = mode_id;
		current_match->pseudomode_id = pseudomode_id;
		current_match->instance_id = instance_id;

		current_match->start = get_epoch_micros();
	}

	void next_activity_span(bigint who_id, short type)
	{
		// If there is an existing activity span for this user then end it
		if(current_activity_spans.find(who_id) != current_activity_spans.end())
			current_activity_spans[who_id]->stop = get_epoch_micros();

		// Bail if we don't have a current match in progress
		if (!current_match) return;

		// Get the activity span pk and bail if one isn't given
		bigint pk = activity_spans_pk_dealer->deal();
		if(pk < 0) return;

		activity_span *as = new activity_span;
		as->id = pk;
		as->who_id = who_id;
		as->match_id = current_match->id;
		as->type = type;

		as->start = get_epoch_micros();

		current_activity_spans[who_id] = as;

		activity_spans.push_back(as);
	}

	void start_capture(bigint who_id, short base_id, int health)
	{
		// Bail if we don't have a current match in progress
		if (!current_match) return;

		// If there is not an existing activity span for this user then return
		if(current_activity_spans.find(who_id) == current_activity_spans.end()) return;

		activity_span *as = current_activity_spans[who_id];

		// Get the next capture event pk and bail if one isn't given
		bigint pk = capture_events_pk_dealer->deal();
		if(pk < 0) return;

		capture_event *ce = new capture_event;
		ce->id = pk;
		ce->who_id = who_id;
		ce->match_id = current_match->id;
		ce->activity_span_id = as->id;
		ce->start = get_epoch_micros();
		ce->base_id = base_id;
		ce->start_health = health;

		std::pair<bigint, short> ck = std::make_pair(who_id, base_id);

		pending_captures[ck] = ce;
	}

	void stop_capture(bigint who_id, short base_id, bool complete, int health)
	{
		std::pair<bigint, short> ck = std::make_pair(who_id, base_id);

		if(pending_captures.find(ck) == pending_captures.end()) return;

		capture_event *ce = pending_captures[ck];

		ce->complete = complete;
		ce->stop_health = health;
		ce->stop = get_epoch_micros();

		capture_events.push_back(ce);
	}

	void add_shot_event(bigint who_id, int game_shot_id, short gun_id)
	{
		// Bail if we don't have a current match in progress
		if (!current_match) return;

		// If there is not an existing activity span for this user then return
		if(current_activity_spans.find(who_id) == current_activity_spans.end()) return;

		activity_span *as = current_activity_spans[who_id];

		// Get the next shot event pk and bail if one isn't given
		bigint pk = shot_events_pk_dealer->deal();
		if(pk < 0) return;

		shot_event *se = new shot_event;
		se->id = pk;
		se->who_id = who_id;
		se->match_id = current_match->id;
		se->gun_id = gun_id;
		se->activity_span_id = as->id;

		se->when = get_epoch_micros();

		pending_shots[std::make_pair(who_id, game_shot_id)] = se;

		shot_events.push_back(se);
	}

	void add_death_event(bigint who_id, int game_shot_id, bigint killer_id, bool teamdeath, bool spawnkill, short botskill)
	{
		// Bail if we don't have a current match in progress
		if (!current_match) return;

		// If there is not an existing activity span for this user then return
		if(current_activity_spans.find(who_id) == current_activity_spans.end()) return;

		activity_span *as = current_activity_spans[who_id];

		// Get the next shot event pk and bail if one isn't given
		bigint pk = death_events_pk_dealer->deal();
		if(pk < 0) return;

		death_event *de = new death_event;
		de->id = pk;
		de->who_id = who_id;
		de->match_id = current_match->id;
		de->activity_span_id = as->id;

		de->when = get_epoch_micros();

		std::pair<bigint, int> ksk = std::make_pair(killer_id, game_shot_id);
		if(pending_shots.find(ksk) != pending_shots.end())
			de->shot_id = pending_shots[ksk]->id;

		de->killer_id = killer_id;
		de->teamdeath = teamdeath;
		de->spawnkill = spawnkill;
		de->botskill = de->botskill;

		death_events.push_back(de);
	}

	void add_frag_event(bigint who_id, int game_shot_id, bigint target_id, bool teamkill, bool spawnkill, short botskill)
	{
		// Bail if we don't have a current match in progress
		if (!current_match) return;

		// If there is not an existing activity span for this user then return
		if(current_activity_spans.find(who_id) == current_activity_spans.end()) return;

		activity_span *as = current_activity_spans[who_id];

		// Get the next shot event pk and bail if one isn't given
		bigint pk = frag_events_pk_dealer->deal();
		if(pk < 0) return;

		frag_event *fe = new frag_event;
		fe->id = pk;
		fe->who_id = who_id;
		fe->match_id = current_match->id;
		fe->activity_span_id = as->id;

		fe->when = get_epoch_micros();

		std::pair<bigint, int> ksk = std::make_pair(who_id, game_shot_id);
		if(pending_shots.find(ksk) != pending_shots.end())
			fe->shot_id = pending_shots[ksk]->id;

		fe->target_id = target_id;
		fe->teamkill = teamkill;
		fe->spawnkill = spawnkill;
		fe->botskill = botskill;

		frag_events.push_back(fe);
	}

	void add_damage_dealt_event(bigint who_id, int game_shot_id, bigint target_id, int damage, int distance)
	{
		// Bail if we don't have a current match in progress
		if (!current_match) return;

		// If there is not an existing activity span for this user then return
		if(current_activity_spans.find(who_id) == current_activity_spans.end()) return;

		activity_span *as = current_activity_spans[who_id];

		// Get the next shot event pk and bail if one isn't given
		bigint pk = damage_dealt_events_pk_dealer->deal();
		if(pk < 0) return;

		damage_dealt_event *dde = new damage_dealt_event;
		dde->id = pk;
		dde->who_id = who_id;
		dde->match_id = current_match->id;
		dde->activity_span_id = as->id;

		dde->when = get_epoch_micros();

		std::pair<bigint, int> ksk = std::make_pair(who_id, game_shot_id);
		if(pending_shots.find(ksk) != pending_shots.end())
			dde->shot_id = pending_shots[ksk]->id;

		dde->target_id = target_id;
		dde->damage = damage;
		dde->distance = distance;

		damage_dealt_events.push_back(dde);
	}

	void end_match()
	{
		current_match->stop = get_epoch_micros();

		dump_stats();

		current_match = NULL;

		activity_spans.clear();
		capture_events.clear();
		shot_events.clear();
		damage_dealt_events.clear();
		frag_events.clear();
		death_events.clear();

		current_activity_spans.clear();
		pending_shots.clear();
		pending_captures.clear();
		
		for(unsigned int i=0; i < pk_dealers_count; i++)
		{
			pk_dealers[i].pkd->next_round();
		}
	}
}
