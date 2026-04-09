#!/usr/bin/env bash
# どのディレクトリから実行しても、このスクリプトと同じ場所の test_sysbench_average.sh を使う
cd "$(dirname "$0")" || exit 1

# cloudlab
export LUA_PATH="/users/Morisaki/sysbench_binary_mysql/share/sysbench/?.lua;/users/Morisaki/sysbench_binary_mysql/share/sysbench/?/init.lua:${LUA_PATH}"
# ann server
#export LUA_PATH="/home/morisaki/sysbench_binary_mysql/share/sysbench/?.lua;/home/morisaki/sysbench_binary_mysql/share/sysbench/?/init.lua:${LUA_PATH}"

./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=default delay=6 multiplier=50 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=delay_0 delay=0 multiplier=50 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
# ./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_1 delay=6 multiplier=1 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
# ./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_2 delay=6 multiplier=2 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
# ./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_4 delay=6 multiplier=4 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_8 delay=6 multiplier=8 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
# ./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_16 delay=6 multiplier=16 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_32 delay=6 multiplier=32 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
# ./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_64 delay=6 multiplier=64 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
./test_sysbench_average.sh mysql-db=sbtest table_size=100 rand-type=pareto filename=multiplier_100 delay=6 multiplier=100 spin_loops=30 tables=1 sysbench_threads=5 time=60 runs=5 histogram=off
