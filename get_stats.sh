output_file=$1
SLURM_CLUSTERS="cbsueccosl01"

sacct -M $SLURM_CLUSTERS --starttime=$(date -d "6 months ago" +%Y-%m-%d) --format=JobID,User,Account,JobName,State,Elapsed,CPUTime,MaxRSS,AveRSS,Nodelist,Submit,End -a --delimiter="," -X --parsable2 > $output_file
