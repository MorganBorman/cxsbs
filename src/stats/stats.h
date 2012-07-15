#ifndef SB_STATS_H
#define SB_STATS_H

namespace stats
{
	typedef long long bigint;

	struct match
	{
		bigint id;
		char map_name[33];
		short mode_id;
		short pseudomode_id;
		int instance_id;
		bigint start;
		bigint stop;
	};

	struct activity_span
	{
		bigint id;
		bigint who_id;
		bigint match_id;
		short type;
		bigint start;
		bigint stop;
	};

	struct capture_event
	{
		bigint id;
	    bigint who_id;
	    bigint match_id;
	    bigint activity_span_id;
	    bigint start;
		bigint stop;
	    short base_id;
	    bool complete;
	    int start_health;
	    int stop_health;
	};

	struct shot_event
	{
		bigint id;
		bigint who_id;
		bigint match_id;
	    short gun_id;
		bigint activity_span_id;
		bigint when;
		bool quad;
	};

	struct damage_dealt_event
	{
		bigint id;
		bigint who_id;
		bigint match_id;
		bigint target_id;
		bigint shot_id;
		bigint activity_span_id;
	    int damage;
	    bigint when;
	    int distance;
	};

	struct death_event
	{
		bigint id;
		bigint who_id;
		bigint match_id;
		bigint killer_id;
		bigint shot_id;
		bigint activity_span_id;
		bigint when;
	    bool teamdeath;
	    short botskill;
	    bool spawnkill;
	};

	struct frag_event
	{
		bigint id;
		bigint who_id;
		bigint match_id;
		bigint shot_id;
		bigint activity_span_id;
		bigint target_id;
		bigint when;
	    bool teamkill;
	    short botskill;
	    bool spawnkill;
	};

	void initialize();

	void update();

	void start_match(short mode_id, char *map_name, short pseudomode_id, int instance_id);

	extern int SPAWNKILL_INTERVAL;
	
	enum {ACTIVITY_SPAN_ALIVE, ACTIVITY_SPAN_DEAD, ACTIVITY_SPAN_SPECTATOR, ACTIVITY_SPAN_INVISIBLE, ACTIVITY_SPAN_DISCONNECT};

	void next_activity_span(bigint who_id, short type);

	void start_capture(bigint who_id, short team, int health);

	void stop_capture(bigint who_id, bool complete, int health);

	void add_shot_event(bigint who_id, int game_shot_id, short gun_id, bool quad);

	void add_death_event(bigint who_id, int game_shot_id, bigint killer_id, bool teamdeath, bool spawnkill, short botskill);

	void add_frag_event(bigint who_id, int game_shot_id, bigint target_id, bool teamkill, bool spawnkill, short botskill);

	void add_damage_dealt_event(bigint who_id, int game_shot_id, bigint target_id, int damage, int distance);

	void end_match();
}

#endif
