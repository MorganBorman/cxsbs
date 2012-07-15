
	void dump_stats()
	{
		// Package all the stats data into an event and pass it to Python
		PyObject *stats_data = PyDict_New();

		PyObject *matches_data = PyTuple_New(1);
		PyDict_SetItemString(stats_data, "matches", matches_data);
		{
			PyObject *match_data = PyDict_New();
			PyDict_SetItemString(match_data, "id", 				PyLong_FromLongLong(	current_match->id));
			PyDict_SetItemString(match_data, "map_name", 		PyString_FromString(	current_match->map_name));
			PyDict_SetItemString(match_data, "mode_id", 		PyInt_FromLong(			current_match->mode_id));
			PyDict_SetItemString(match_data, "pseudomode_id", 	PyInt_FromLong(			current_match->pseudomode_id));
			PyDict_SetItemString(match_data, "instance_id", 	PyInt_FromLong(			current_match->instance_id));
			PyDict_SetItemString(match_data, "start", 			PyLong_FromLongLong(	current_match->start));
			PyDict_SetItemString(match_data, "stop", 			PyLong_FromLongLong(	current_match->stop));
			PyTuple_SetItem(matches_data, 0, match_data);
			delete current_match;
		}

		PyObject *activity_spans_data = PyTuple_New(activity_spans.size());
		PyDict_SetItemString(stats_data, "activity_spans", activity_spans_data);
		for(unsigned int i = 0; i < activity_spans.size(); i++)
		{
			activity_span *as = activity_spans[i];

			PyObject *asd = PyDict_New();
			PyDict_SetItemString(asd, "id", 					PyLong_FromLongLong(	as->id));
			PyDict_SetItemString(asd, "who_id", 				PyLong_FromLongLong(	as->who_id));
			PyDict_SetItemString(asd, "match_id", 				PyLong_FromLongLong(	as->match_id));
			PyDict_SetItemString(asd, "type", 					PyInt_FromLong(			as->type));
			PyDict_SetItemString(asd, "start", 					PyLong_FromLongLong(	as->start));
			PyDict_SetItemString(asd, "stop", 					PyLong_FromLongLong(	as->stop));
			PyTuple_SetItem(activity_spans_data, i, asd);
			delete as;
		}

		PyObject *capture_events_data = PyTuple_New(capture_events.size());
		PyDict_SetItemString(stats_data, "capture_events", capture_events_data);
		for(unsigned int i = 0; i < capture_events.size(); i++)
		{
			capture_event *ce = capture_events[i];
			
			PyObject *ced = PyDict_New();
			PyDict_SetItemString(ced, "id", 					PyLong_FromLongLong(	ce->id));
			PyDict_SetItemString(ced, "who_id",					PyLong_FromLongLong(	ce->who_id));
			PyDict_SetItemString(ced, "match_id", 				PyLong_FromLongLong(	ce->match_id));
			PyDict_SetItemString(ced, "activity_span_id", 		PyLong_FromLongLong(	ce->activity_span_id));
			PyDict_SetItemString(ced, "start", 					PyLong_FromLongLong(	ce->start));
			PyDict_SetItemString(ced, "stop", 					PyLong_FromLongLong(	ce->stop));
			PyDict_SetItemString(ced, "base_id", 				PyInt_FromLong(			ce->base_id));
			PyDict_SetItemString(ced, "complete", 										ce->complete ? Py_True : Py_False);
			Py_INCREF(PyDict_GetItemString(ced, "complete"));
			PyDict_SetItemString(ced, "start_health", 			PyInt_FromLong(			ce->start_health));
			PyDict_SetItemString(ced, "stop_health", 			PyInt_FromLong(			ce->stop_health));
			PyTuple_SetItem(capture_events_data, i, ced);
			delete ce;
		}
		
		PyObject *shot_events_data = PyTuple_New(shot_events.size());
		PyDict_SetItemString(stats_data, "shot_events", shot_events_data);
		for(unsigned int i = 0; i < shot_events.size(); i++)
		{
			shot_event *se = shot_events[i];

			PyObject *sed = PyDict_New();
			PyDict_SetItemString(sed, "id", 					PyLong_FromLongLong(	se->id));
			PyDict_SetItemString(sed, "who_id", 				PyLong_FromLongLong(	se->who_id));
			PyDict_SetItemString(sed, "match_id", 				PyLong_FromLongLong(	se->match_id));
			PyDict_SetItemString(sed, "gun_id", 				PyInt_FromLong(			se->gun_id));
			PyDict_SetItemString(sed, "activity_span_id", 		PyLong_FromLongLong(	se->activity_span_id));
			PyDict_SetItemString(sed, "when", 					PyLong_FromLongLong(	se->when));
			PyTuple_SetItem(activity_spans_data, i, sed);
			delete se;
		}
		
		PyObject *damage_dealt_events_data = PyTuple_New(damage_dealt_events.size());
		PyDict_SetItemString(stats_data, "damage_dealt_events", damage_dealt_events_data);
		for(unsigned int i = 0; i < damage_dealt_events.size(); i++)
		{
			damage_dealt_event *dde = damage_dealt_events[i];

			PyObject *dded = PyDict_New();
			PyDict_SetItemString(dded, "id", 					PyLong_FromLongLong(	dde->id));
			PyDict_SetItemString(dded, "who_id", 				PyLong_FromLongLong(	dde->who_id));
			PyDict_SetItemString(dded, "match_id", 				PyLong_FromLongLong(	dde->match_id));
			PyDict_SetItemString(dded, "shot_id", 				PyLong_FromLongLong(	dde->shot_id));
			PyDict_SetItemString(dded, "damage", 				PyInt_FromLong(			dde->damage));
			PyDict_SetItemString(dded, "distance", 				PyInt_FromLong(			dde->distance));
			PyDict_SetItemString(dded, "activity_span_id", 		PyLong_FromLongLong(	dde->activity_span_id));
			PyDict_SetItemString(dded, "when", 					PyLong_FromLongLong(	dde->when));
			PyTuple_SetItem(damage_dealt_events_data, i, dded);
			delete dde;
		}
		
		PyObject *death_events_data = PyTuple_New(death_events.size());
		PyDict_SetItemString(stats_data, "death_events", death_events_data);
		for(unsigned int i = 0; i < death_events.size(); i++)
		{
			death_event *de = death_events[i];

			PyObject *ded = PyDict_New();
			PyDict_SetItemString(ded, "id", 					PyLong_FromLongLong(	de->id));
			PyDict_SetItemString(ded, "who_id", 				PyLong_FromLongLong(	de->who_id));
			PyDict_SetItemString(ded, "match_id", 				PyLong_FromLongLong(	de->match_id));
			PyDict_SetItemString(ded, "killer_id", 				PyLong_FromLongLong(	de->killer_id));
			PyDict_SetItemString(ded, "shot_id", 				PyLong_FromLongLong(	de->shot_id));
			PyDict_SetItemString(ded, "activity_span_id", 		PyLong_FromLongLong(	de->activity_span_id));
			PyDict_SetItemString(ded, "when", 					PyLong_FromLongLong(	de->when));
			PyDict_SetItemString(ded, "botskill", 				PyInt_FromLong(			de->botskill));
			PyDict_SetItemString(ded, "teamdeath", 										de->teamdeath ? Py_True : Py_False);
			Py_INCREF(PyDict_GetItemString(ded, "teamdeath"));
			PyDict_SetItemString(ded, "spawnkill", 										de->spawnkill ? Py_True : Py_False);
			Py_INCREF(PyDict_GetItemString(ded, "spawnkill"));
			PyTuple_SetItem(death_events_data, i, ded);
			delete de;
		}
		
		PyObject *frag_events_data = PyTuple_New(frag_events.size());
		PyDict_SetItemString(stats_data, "frag_events", frag_events_data);
		for(unsigned int i = 0; i < frag_events.size(); i++)
		{
			frag_event *fe = frag_events[i];

			PyObject *fed = PyDict_New();
			PyDict_SetItemString(fed, "id", 					PyLong_FromLongLong(	fe->id));
			PyDict_SetItemString(fed, "who_id", 				PyLong_FromLongLong(	fe->who_id));
			PyDict_SetItemString(fed, "match_id", 				PyLong_FromLongLong(	fe->match_id));
			PyDict_SetItemString(fed, "target_id", 				PyLong_FromLongLong(	fe->target_id));
			PyDict_SetItemString(fed, "shot_id", 				PyLong_FromLongLong(	fe->shot_id));
			PyDict_SetItemString(fed, "activity_span_id", 		PyLong_FromLongLong(	fe->activity_span_id));
			PyDict_SetItemString(fed, "when", 					PyLong_FromLongLong(	fe->when));
			PyDict_SetItemString(fed, "botskill", 				PyInt_FromLong(			fe->botskill));
			PyDict_SetItemString(fed, "teamkill", 										fe->teamkill ? Py_True : Py_False);
			Py_INCREF(PyDict_GetItemString(fed, "teamkill"));
			PyDict_SetItemString(fed, "spawnkill", 										fe->spawnkill ? Py_True : Py_False);
			Py_INCREF(PyDict_GetItemString(fed, "spawnkill"));
			PyTuple_SetItem(frag_events_data, i, fed);
			delete fe;
		}
	}
