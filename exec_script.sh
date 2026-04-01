#!/usr/bin/env bash
# どのディレクトリから実行しても、このスクリプトと同じ場所の test_sysbench_average.sh を使う
cd "$(dirname "$0")" || exit 1

export LUA_PATH="/users/Morisaki/sysbench_binary_mysql/share/sysbench/?.lua;/users/Morisaki/sysbench_binary_mysql/share/sysbench/?/init.lua:${LUA_PATH}"

./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=baseline tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=delay_0 delay=0 multiplier=50 spin_loops=30 tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_5_delay_6 delay=6 multiplier=5 spin_loops=30 tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_5_delay_5 delay=5 multiplier=5 spin_loops=30 tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_5_delay_4 delay=4 multiplier=5 spin_loops=30 tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_5_delay_3 delay=3 multiplier=5 spin_loops=30 tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_5_delay_2 delay=2 multiplier=5 spin_loops=30 tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_5_delay_1 delay=1 multiplier=5 spin_loops=30 tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 histogram=off
