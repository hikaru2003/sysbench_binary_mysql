#! /bin/bash

#usage:
<< COMMENT
基本的には上の二行のみ編集すればいい（三行目はデフォルト値でいい）
./test_sysbench_average.sh mysql-db=sbtest_100 table_size=100 rand-type=pareto filename= \
delay=6 multiplier=50 spin_loops=30 \
tables=1 threads=32 time=60 runs=10 read_threads=4 write_threads=4 
COMMENT

set -euo pipefail

# コア0以外の全コアを taskset で指定する（0..N-1 が連続している前提）
ALL_CPUS="$(nproc --all)"
if (( ALL_CPUS <= 1 )); then
    TASKSET_CPUS="0"
else
    TASKSET_CPUS="1-$((ALL_CPUS-1))"
fi

function test_() {
    # デフォルト値
    local tables=1
    local table_size=100000
    local threads=32
    local time=60
    local rand_type=pareto
    local filename=tmp
    local db="${SB_DB:-sbtest}"
    local runs=10
    local innodb_read_io_threads=4
    local innodb_write_io_threads=4
    local innodb_spin_wait_delay=6
    local innodb_spin_wait_pause_multiplier=50
    local innodb_sync_spin_loops=30

    # 引数 (例: tables=2 threads=64 rand-type=uniform db=mydb) で上書き
    for arg in "$@"; do
        case "$arg" in
            tables=*)
                tables="${arg#*=}"
                ;;
            table_size=*)
                table_size="${arg#*=}"
                ;;
            threads=*)
                threads="${arg#*=}"
                ;;
            time=*)
                time="${arg#*=}"
                ;;
            rand-type=*)
                rand_type="${arg#*=}"
                ;;
            filename=*)
                filename="${arg#*=}"
                ;;
            mysql-db=*)
                db="${arg#*=}"
                ;;
            runs=*)
                runs="${arg#*=}"
                ;;
            read_threads=*)
                innodb_read_io_threads="${arg#*=}"
                ;;
            write_threads=*)
                innodb_write_io_threads="${arg#*=}"
                ;;
            delay=*)
                innodb_spin_wait_delay="${arg#*=}"
                ;;
            multiplier=*)
                innodb_spin_wait_pause_multiplier="${arg#*=}"
                ;;
            spin_loops=*)
                innodb_sync_spin_loops="${arg#*=}"
                ;;
            *)
                echo "不明なパラメータです: $arg" >&2
                ;;
        esac
    done

    if [[ -z "${filename}" ]]; then
        echo "エラー: filename が空です。例: filename=sbtest_10000_table_size_100_delay_6 のように指定してください。" >&2
        exit 1
    fi

    local out_dir="${filename}"
    local out_tsv="${out_dir}/metrics.tsv"
    local out_summary="${out_dir}/summary.txt"

    mkdir -p "${out_dir}"

    {
        echo "# Environmental Setting
- innodb_read_io_threads = ${innodb_read_io_threads}
- innodb_write_io_threads = ${innodb_write_io_threads}
- innodb_spin_wait_delay = ${innodb_spin_wait_delay}
- innodb_spin_wait_pause_multiplier = ${innodb_spin_wait_pause_multiplier}
- innodb_sync_spin_loops = ${innodb_sync_spin_loops}

# Command
 $> taskset -c ${TASKSET_CPUS} sysbench oltp_read_write --mysql-db=${db} --tables=${tables} --table_size=${table_size} --threads=${threads} --time=${time} --rand-type=${rand_type} run

# Output
- metrics: ${out_tsv}
- summary: ${out_summary}
- raw logs: ${out_dir}/run<N>.txt
"
    } > "${out_summary}"

    printf "run\ttransactions_per_sec\tqueries_per_sec\tlatency_avg_ms\tlatency_p95_ms\tlatency_min_ms\tlatency_max_ms\ttotal_time_s\terrors_per_sec\n" > "${out_tsv}"

    # 実験開始前に InnoDB のスピン待ちパラメータをセット
    sudo mysql -e "SET GLOBAL innodb_spin_wait_delay = ${innodb_spin_wait_delay}; SET GLOBAL innodb_spin_wait_pause_multiplier = ${innodb_spin_wait_pause_multiplier}; SET GLOBAL innodb_sync_spin_loops = ${innodb_sync_spin_loops};"

    local i
    for ((i=1; i<=runs; i++)); do
        local raw="${out_dir}/run${i}.txt"

        {
            echo "# run=${i}/${runs}"
            echo "# $(date -Iseconds)"
            echo "# cmd: taskset -c ${TASKSET_CPUS} sysbench oltp_read_write --mysql-db=${db} --tables=${tables} --table_size=${table_size} --threads=${threads} --time=${time} --rand-type=${rand_type} run"
            echo
        } > "${raw}"

        taskset -c "${TASKSET_CPUS}" ./bin/sysbench ./share/sysbench/oltp_read_write.lua \
            --mysql-host=localhost \
            --mysql-port=3306 \
            --mysql-user=sbuser \
            --mysql-password=password \
            --mysql-db="$db" \
            --tables="$tables" \
            --table_size="$table_size" \
            --threads="$threads" \
            --time="$time" \
            --rand-type="$rand_type" \
            run >> "${raw}"

        # sysbench 1.0.x の典型出力（"(265.37 per sec.)" または "([269.95 per sec.)" の両対応）
        local tps qps avg p95 min max total_time eps
        tps="$(awk '/transactions:/{for(i=1;i<=NF;i++){if($i ~ /^\(\[?[0-9.]+$/){gsub(/[^0-9.]/,"",$i); print $i; exit}}}' "${raw}")"
        qps="$(awk '/queries:/{for(i=1;i<=NF;i++){if($i ~ /^\([0-9.]+$/){gsub(/[^0-9.]/,"",$i); print $i; exit}}}' "${raw}")"
        eps="$(awk '/ignored errors:/{for(i=1;i<=NF;i++){if($i ~ /^\([0-9.]+$/){gsub(/[^0-9.]/,"",$i); print $i; exit}}}' "${raw}")"
        total_time="$(awk '/total time:/{gsub(/s/,"",$3); print $3; exit}' "${raw}")"

        min="$(awk '/Latency \(ms\):/{flag=1; next} flag && $1=="min:"{print $2; exit}' "${raw}")"
        avg="$(awk '/Latency \(ms\):/{flag=1; next} flag && $1=="avg:"{print $2; exit}' "${raw}")"
        max="$(awk '/Latency \(ms\):/{flag=1; next} flag && $1=="max:"{print $2; exit}' "${raw}")"
        p95="$(awk '/Latency \(ms\):/{flag=1; next} flag && $1=="95th"{print $3; exit}' "${raw}")"

        if [[ -z "${tps}" || -z "${avg}" ]]; then
            echo "run ${i}: 指標抽出に失敗しました。raw log: ${raw}" >&2
            exit 1
        fi

        printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
            "${i}" "${tps:-NA}" "${qps:-NA}" "${avg:-NA}" "${p95:-NA}" "${min:-NA}" "${max:-NA}" "${total_time:-NA}" "${eps:-NA}" \
            >> "${out_tsv}"
    done

    # 集計（NA は無視）。平均のみ（必要なら後で中央値など追加可能）
    {
        echo
        echo "## Extracted metrics (TSV)"
        echo "${out_tsv}"
        echo
        awk -F'\t' '
            NR==1{next}
            {
                if($2!="NA"){tps+=$2; n_tps++}
                if($3!="NA"){qps+=$3; n_qps++}
                if($4!="NA"){lat+=$4; n_lat++}
                if($5!="NA"){p95+=$5; n_p95++}
                if($8!="NA"){tt+=$8; n_tt++}
                if($9!="NA"){eps+=$9; n_eps++}
            }
            END{
                printf("runs=%d\n", NR-1)
                if(n_tps) printf("TPS_avg=%.4f\n", tps/n_tps)
                if(n_qps) printf("QPS_avg=%.4f\n", qps/n_qps)
                if(n_lat) printf("Latency_avg_ms=%.4f\n", lat/n_lat)
                if(n_p95) printf("Latency_p95_ms_avg=%.4f\n", p95/n_p95)
                if(n_tt) printf("Total_time_s_avg=%.4f\n", tt/n_tt)
                if(n_eps) printf("Ignored_errors_per_sec_avg=%.4f\n", eps/n_eps)
            }
        ' "${out_tsv}"
    } >> "${out_summary}"
}

# スクリプトとして実行された場合はコマンドライン引数をそのまま渡す
test_ "$@"
