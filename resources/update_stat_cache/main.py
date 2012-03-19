import datetime, math
from database import 	sessionFactory, tableSettings, NoResultFound, \
						User, UserStatCache, UserConnection, DeathEvent, FragEvent, DamageDealtEvent, DamageSpentEvent, \
						NOTUSER, TEAMKILL, SUICIDE

epoch = datetime.datetime.utcfromtimestamp(0)
today = datetime.datetime.today()
today_delta = today - epoch

STARTING_RANK_POINTS = 1000

def get_frag_delta(killer_rank_points, killee_rank_points):
	rank_point_difference = math.fabs(killer_rank_points - killee_rank_points)
	delta = 10 * max(0.1, math.log(rank_point_difference, 2))
	return delta

def get_death_delta(killee_rank_points, killer_rank_points):
	rank_point_difference = math.fabs(killer_rank_points - killee_rank_points)
	delta = -10 * max(0.1, math.log(rank_point_difference, 2))
	return delta

def get_suicide_delta(user_rank_points):
	return -2

def get_teamkill_delta(user_rank_points):
	return -10

def get_notuser_delta(user_rank_points):
	return 1

def get_user_ids():
	'''
	Returns a list of all unique userId values.
	'''
	session = sessionFactory()
	try:
		ids = []
		results = session.query(User).all()
		for user in results:
			ids.append(user.id)
		return ids
	finally:
		session.close()
		
def get_cached_rank_points(userId, day):
	'''
	Returns the cache entry for the specified userId and day
	Or None if one does not exist.
	'''
	session = sessionFactory()
	try:
		results = session.query(UserStatCache).filter(UserStatCache.userId==userId).filter(UserStatCache.day==day).one()
		return results.rank_points
	except NoResultFound:
		return None
	finally:
		session.close()

def get_first_day(userId):
	'''
	Returns the first day on which the user in question has any entries in the tables for frags, deaths, teamkills, or suicides.
	'''
	
	query_text = """
	SELECT min(timestamp) AS timestamp
	FROM ((	
			SELECT min(timestamp) AS timestamp
			FROM %s
			WHERE "userId" = :user
		) 
		UNION
		(
			SELECT min(timestamp) AS timestamp
			FROM %s
			WHERE "userId" = :user
		)) AS first_events;
	""" % (tableSettings['frag_event_table_name'], tableSettings['death_event_table_name'])
	
	session = sessionFactory()
	try:
		first_timestamp = session.query("timestamp").from_statement(query_text).params(user=userId).one()
		if first_timestamp.timestamp is None:
			raise NoResultFound()
		first_datetime = datetime.datetime.fromtimestamp(first_timestamp.timestamp)
		first_delta = first_datetime - epoch
		return first_delta.days
	except NoResultFound:
		return today_delta.days
	finally:
		session.close()

def get_rank(userId, day):
	'''
	Returns the cached rank for a userId and a day. If one does not exist a call will be made to the calculate_up_to() function and then the newly cached value will be returned.
	'''
	if day < get_first_day(userId):
		return STARTING_RANK_POINTS
	else:
		return calculate_up_to(userId, day)

def calculate_up_to(userId, day):
	'''
	Calculates the ranking_points and caches them by getting the previous day and for each frag, death, teamkill and suicide 
	then calculating the effect that has on the total ranking_points.
	
	This will get called recursively many times since each depends on all the days before it and all the other player's rankings, which depend on the days before them.
	But since each call to this function caches the value, the total number of expensive calls to this query should only be O(days*users).
	
	This function actually has the job of maintaining the stat_cache table.
	No other function writes to that table.
	
	Returns the cached rank for this userId and day.
	'''
	current_rank_points = get_cached_rank_points(userId, day)
	if current_rank_points is not None:
		return current_rank_points
	else:
		previous_rank = get_rank(userId, day - 1)
		new_rank = calculate_new_rank(userId, previous_rank, day)
		session = sessionFactory()
		try:
			entry = UserStatCache(userId, day, new_rank)
			session.add(entry)
			session.commit()
		finally:
			session.close()
		return new_rank

def calculate_new_rank(userId, start_rank, day):
	'''
	Get the frag, death, teamkill, and suicide entries for the userId specified for the day specified.
	Calculate a delta stat_points and add it to the start_rank.
	Return that value.
	'''
	running_rank_points = start_rank
	running_rank_points = get_and_apply_frags(userId, running_rank_points, day)
	running_rank_points = get_and_apply_deaths(userId, running_rank_points, day)
	return running_rank_points
	
def get_and_apply_frags(userId, running_rank_points, day):
	'''
	Queries the frags, and teamkills from the frag_events table, gets the delta for each one adds them to the running_rank_points then returns the running_rank_points
	'''
	session = sessionFactory()
	try:
		day_start_seconds = (day * 24 * 60 * 60)
		day_end_seconds = ((day+1) * 24 * 60 * 60)
		frag_events = session.query(FragEvent).filter(FragEvent.userId==userId).filter(FragEvent.timestamp>=day_start_seconds).filter(FragEvent.timestamp<day_end_seconds).all()
		for event in frag_events:
			if event.targetId == TEAMKILL:
				running_rank_points += get_teamkill_delta(running_rank_points)
			elif event.targetId == NOTUSER:
				running_rank_points += get_notuser_delta(running_rank_points)
			else:#they got another user
				target_rank_points = get_rank(event.targetId, day-1)
				running_rank_points += get_frag_delta(running_rank_points, target_rank_points)
		return running_rank_points
	finally:
		session.close()

def get_and_apply_deaths(userId, running_rank_points, day):
	'''
	Queries the deaths, and suicides from the frag_events table, gets the delta for each one adds them to the running_rank_points then returns the running_rank_points
	'''
	session = sessionFactory()
	try:
		day_start_seconds = (day * 24 * 60 * 60)
		day_end_seconds = ((day+1) * 24 * 60 * 60)
		frag_events = session.query(DeathEvent).filter(DeathEvent.userId==userId).filter(DeathEvent.timestamp>=day_start_seconds).filter(DeathEvent.timestamp<day_end_seconds).all()
		for event in frag_events:
			if event.causeId == SUICIDE:
				running_rank_points += get_suicide_delta(running_rank_points)
			elif event.causeId == NOTUSER:
				running_rank_points -= get_notuser_delta(running_rank_points)
			else:#they got killed by another user
				cause_rank_points = get_rank(event.causeId, day-1)
				running_rank_points += get_death_delta(running_rank_points, cause_rank_points)
		return running_rank_points
	finally:
		session.close()

def update_cache():
	'''
	Gets the previous days since epoch. Then calls get_rank() on each userId for that day.
	'''
	ids = get_user_ids()
	day = today_delta.days - 1 #we only update the cache for the last full day
	
	for id in ids:
		new_rank = get_rank(id, day)
		print "The new cached rank for userId=%d is: %d" %(id, new_rank)

if __name__ == '__main__':
	update_cache()