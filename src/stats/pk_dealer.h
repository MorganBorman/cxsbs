#ifndef SB_STATS_PK_DEALER_H
#define SB_STATS_PK_DEALER_H

#include <queue>

typedef long long bigint;

struct pk_counter
{
	bigint cur;
	bigint end;
};

class pk_dealer
{
private:
	bool awaiting_pks;
	bigint pks_left;
	bigint pks_this_round;
	bigint round_number;
	bigint pks_per_round[5];
	bigint avg_pks_per_round;
	bigint target_pks_per_round;
	std::queue<pk_counter*> pk_counters;
public:
	pk_dealer(bigint expected_per_round);

	void update_statistics();

	bigint order_pks();

	void next_round();

	void add_counter(bigint cur, bigint end);

	bigint deal();
};

#endif
