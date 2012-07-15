#include "pk_dealer.h"
#include <cassert>

#include <stdio.h>

pk_dealer::pk_dealer(bigint expected_per_round)
{
	awaiting_pks = false;
	pks_left = 0;
	pks_this_round = 0;
	round_number = 0;
	for(short i = 0; i < 5; i++) pks_per_round[i] = expected_per_round;
	update_statistics();
}

void pk_dealer::update_statistics()
{
	fprintf(stderr, "updating statistics:\n");
	bigint sum = 0;
	for(short i = 0; i < 5; i++) sum += pks_per_round[i];
	avg_pks_per_round = (sum/5);
	fprintf(stderr, "\t%lld\n", avg_pks_per_round);
	// Always ask for 10% more than were used on average the last 5 rounds
	target_pks_per_round = avg_pks_per_round + (avg_pks_per_round/10);
	fprintf(stderr, "\t%lld\n", target_pks_per_round);
}

bigint pk_dealer::order_pks()
{
	if(awaiting_pks) return 0;
	// Don't ask for more pks if we still have more than 25% of our target pks left
	if(((pks_left*100)/(target_pks_per_round)) >= 25) return 0;
	// Ask for enough pks to meet our target supply
	bigint order = target_pks_per_round - pks_left;
	if (order > 0)
	{
		awaiting_pks = true;
		return order;
	}
	else return 0;
}

void pk_dealer::next_round()
{
	pks_per_round[round_number] = pks_this_round;
	pks_this_round = 0;
	update_statistics();
}

void pk_dealer::add_counter(bigint cur, bigint end)
{
	pks_left += (end - cur) + 1;
	pk_counter *pkc = new pk_counter;
	pkc->cur = cur;
	pkc->end = end;
	pk_counters.push(pkc);
	awaiting_pks = false;
}

bigint pk_dealer::deal()
{
	// Return an invalid key if there aren't any pk_counters left
	if(!pk_counters.size()) return -1;
	// We should never have an empty pk_counter left on the queue
	assert(pk_counters.front()->cur <= pk_counters.front()->end);
	// Get and increment the current position in the next pk counter
	bigint deal_pk = pk_counters.front()->cur++;
	// Maintain our statistics data
	pks_left--;
	pks_this_round++;
	// If we emptied that pk_counter remove it from the queue
	if(pk_counters.front()->cur > pk_counters.front()->end) pk_counters.pop();
	// Return the next pk
	return deal_pk;
}
