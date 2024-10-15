setlocal enabledelayedexpansion
set "pth_dataset=E:\data"

set "micapipe_dir=micapipe"
set "hippunfold_dir=hippunfold"
set "zbrains_dir=zbrains_newblur"

set "demo_controls=E:\participants_mics_hc.csv"
set "demo_patients=E:\PX_participants.csv"

set "sids=all"
set "sess=all"
call conda activate zbrains
<<<<<<< Updated upstream
call python -m src.zbrains --run "proc" ^
=======
call python -m src.zbrains --run "proc analysis" ^
>>>>>>> Stashed changes
                   --sub "%sids%" ^
                   --micapipe %micapipe_dir% ^
                   --hippunfold %hippunfold_dir% ^
                   --dataset %pth_dataset% ^
                   --zbrains %zbrains_dir% ^
                   --demo_ref %demo_controls% ^
                   --dataset_ref %pth_dataset% ^
                   --zbrains_ref %zbrains_dir% ^
                   --smooth_ctx 5 ^
                   --smooth_hip 2 ^
                   --n_jobs 4 ^
                   --n_jobs_wb 4 ^
<<<<<<< Updated upstream
                   --dicoms 0 ^
                   --volumetric 0 ^
                   --struct cortex ^
                   --feat qT1_blur flair_blur ^
=======
                   --dicoms 1 ^
>>>>>>> Stashed changes
		           --label_ctx "white" ^
                   --wb_path "C:/Users/Ian/Downloads/workbench-windows64-v1.5.0/workbench/bin_windows64" ^
                   --column_map participant_id=ID session_id=SES ^
                   --verbose 2
    )
pause