import argparse
import os
import sys
from functions.utilities import show_title, show_note, show_error, show_info, show_warning, do_cmd, parse_option_single_value, parse_option_multiple_values, allowed_to_regex
import subprocess
from functions.new_constants import *
import time


# # Parse arguments
# parser = argparse.ArgumentParser()
# parser.add_argument('--struct', required=True, choices=LIST_STRUCTURES)
# parser.add_argument('--feat', nargs='+', required=True, choices=LIST_FEATURES)
# parser.add_argument('--fwhm')
# parser.add_argument('--tmp', required=True)
# parser.add_argument('--resolution', nargs='+', choices=LIST_RESOLUTIONS)
# parser.add_argument('--labels', nargs='+')
# args = parser.parse_args()



def map_subcortex(bids_id, feat, subject_surf_dir, subject_micapipe_dir, subject_output_dir, folder_maps, folder_sctx, script_dir):
    show_info(f"{bids_id}: Mapping '{feat}' to subcortical structures")

    map_output = {'volume': 'volume', 'flair': 'flair', 'adc': 'ADC', 'fa': 'FA', 'qt1': 'T1map'}

    # Input & output locations
    aseg_stats_file = os.path.join(subject_surf_dir, "stats", "aseg.stats")
    seg_file = os.path.join(subject_micapipe_dir, "parc", f"{bids_id}_space-nativepro_T1w_atlas-subcortical.nii.gz")
    input_dir = os.path.join(subject_micapipe_dir, "maps")
    output_dir = os.path.join(subject_output_dir, folder_maps, folder_sctx)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{bids_id}_feature-{map_output[feat.lower()]}.csv")

    # check that input files exist & if not volume
    if feat != "volume":
        # Mappings from features names to the way they appear in the input and output filenames
        map_input = {'flair': 'map-flair', 'adc': 'model-DTI_map-ADC', 'fa': 'model-DTI_map-FA', 'qt1': 'map-T1map'}
        input_file = os.path.join(input_dir, f"{bids_id}_space-nativepro_{map_input[feat.lower()]}.nii.gz")

        for file in [seg_file, input_file]:
            if not os.path.isfile(file):
                show_warning(f"{bids_id}: cannot map '{feat}' to subcortical structures. Missing file: {file}")
                return

        subprocess.run(["python", os.path.join(script_dir, "subcortical_mapping.py"), "-id", bids_id, "-i", input_file, "-s", seg_file, "-o", output_file])

    else:
        if not os.path.isfile(aseg_stats_file):
            show_warning(f"{bids_id}: cannot map '{feat}' to subcortical structures. Missing file {aseg_stats_file}")
            return

        subprocess.run(["python", os.path.join(script_dir, "subcortical_mapping.py"), "-id", bids_id, "-v", aseg_stats_file, "-o", output_file])

    if os.path.isfile(output_file):
        show_note(f"{bids_id}: '{feat}' successfully mapped.")
    else:
        show_warning(f"{bids_id}: could not map '{feat}' to subcortical structures.")

def map_cortex(bids_id, feat, resol, label="white", fwhm=None, workbench_path=None, subject_micapipe_dir=None, subject_output_dir=None, folder_maps=None, folder_ctx=None):
    show_info(f"{bids_id}: Mapping '{feat}' to cortex [label={label}, resolution={resol}]")

    # Input & output locations
    surf_dir = os.path.join(subject_micapipe_dir, "surf")
    input_dir = os.path.join(subject_micapipe_dir, "maps")
    output_dir = os.path.join(subject_output_dir, folder_maps, folder_ctx)
    os.makedirs(output_dir, exist_ok=True)
    
    # Mappings from features names to the way they appear in the input and output filenames
    map_feat = {'thickness': 'thickness', 'flair': 'flair', 'adc': 'ADC', 'fa': 'FA', 'qt1': 'T1map'}

    # feat name in filenames
    input_feat = map_feat[feat.lower()]
    output_feat = map_feat[feat.lower()]

    n = 0
    for h in ['L', 'R']:
        # Set paths
        surf_file = os.path.join(surf_dir, f"{bids_id}_hemi-{h}_space-nativepro_surf-fsLR-{resol}_label-{label}.surf.gii")

        prefix = f"{bids_id}_hemi-{h}_surf-fsLR-{resol}"
        if feat == "thickness":
            input_file = os.path.join(input_dir, f"{prefix}_label-{input_feat}.func.gii")
            output_file = os.path.join(output_dir, f"{prefix}_label-{label}_feature-{output_feat}_smooth-{fwhm}mm.func.gii")
        else:
            input_file = os.path.join(input_dir, f"{prefix}_label-{label}_{input_feat}.func.gii")
            output_file = os.path.join(output_dir, f"{prefix}_label-{label}_feature-{output_feat}_smooth-{fwhm}mm.func.gii")

        # Check if file exists
        for file in [surf_file, input_file]:
            if not os.path.isfile(file):
                show_warning(f"{bids_id}: cannot map '{feat}' [label={label}, resolution={resol}] to cortex. Missing file: {file}")
                return

        # Perform mapping
        subprocess.run([os.path.join(workbench_path, "wb_command"), "-metric-smoothing", surf_file, input_file, str(fwhm), output_file])
        if os.path.isfile(output_file):
            n += 1

    if n == 2:
        show_note(f"{bids_id}: '{feat}' [label={label}, resolution={resol}] successfully mapped.")
    else:
        show_warning(f"{bids_id}: could not map '{feat}' [label={label}, resolution={resol}] to cortex.")
        
def map_hippocampus(bids_id, feat, resol, label="midthickness", workbench_path=None, subject_hippunfold_dir=None, subject_micapipe_dir=None, subject_output_dir=None, folder_maps=None, folder_hip=None, fwhm=None):
    show_info(f"{bids_id}: Mapping '{feat}' to hippocampus [label={label}, resolution={resol}]")

    # Input & output locations
    surf_dir = os.path.join(subject_hippunfold_dir, "surf")
    input_dir = os.path.join(subject_micapipe_dir, "maps")
    output_dir = os.path.join(subject_output_dir, folder_maps, folder_hip)
    os.makedirs(output_dir, exist_ok=True)
    
    # Mappings from features names to the way they appear in the input, intermediate and output filenames
    map_input = {'thickness': 'thickness', 'flair': 'map-flair', 'adc': 'model-DTI_map-ADC', 'fa': 'model-DTI_map-FA', 'qt1': 'map-T1map'}
    map_inter = {'thickness': 'thickness', 'flair': 'flair', 'adc': 'ADC', 'fa': 'FA', 'qt1': 'T1map'}
    map_output = {'thickness': 'thickness', 'flair': 'flair', 'adc': 'ADC', 'fa': 'FA', 'qt1': 'T1map'}

    # feat name in filenames
    input_feat = map_input[feat.lower()]
    inter_feat = map_inter[feat.lower()]
    output_feat = map_output[feat.lower()]

    n = 0
    for h in ['L', 'R']:
        # Set paths
        prefix = f"{bids_id}_hemi-{h}"

        surf_file = os.path.join(surf_dir, f"{prefix}_space-T1w_den-{resol}_label-hipp_{label}.surf.gii")
        input_file = os.path.join(input_dir, f"{bids_id}_space-nativepro_{input_feat}.nii.gz") # Not used for thickness
        if feat == "thickness":
            inter_file = os.path.join(surf_dir, f"{prefix}_space-T1w_den-{resol}_label-hipp_thickness.shape.gii")
        else:
            inter_file = os.path.join(surf_dir, f"{prefix}_space-T1w_desc-{inter_feat}_den-{resol}_feature-hipp_{label}.func.gii")
        output_file = os.path.join(output_dir, f"{prefix}_den-{resol}_label-{label}_feature-{output_feat}_smooth-{fwhm}mm.func.gii")

        # Check if file exists
        check_file = input_file if feat != "thickness" else inter_file
        for file in [surf_file, check_file]:
            if not os.path.isfile(file):
                show_warning(f"{bids_id}: cannot map '{feat}' [label={label}, resolution={resol}] to hippocampus. Missing file: {file}")
                return

        # Perform mapping
        if feat != "thickness":
            subprocess.run([os.path.join(workbench_path, "wb_command"), "-volume-to-surface-mapping", input_file, surf_file, inter_file, "-trilinear"])

        subprocess.run([os.path.join(workbench_path, "wb_command"), "-metric-smoothing", surf_file, inter_file, str(fwhm), output_file])

        if os.path.isfile(output_file):
            n += 1

    if n == 2:
        show_note(f"{bids_id}: '{feat}' [label={label}, resolution={resol}] successfully mapped.")
    else:
        show_warning(f"{bids_id}: could not map '{feat}' [label={label}, resolution={resol}] to hippocampus.")

def run(structure, features, tmp_dir, WORKBENCH_PATH, subject_micapipe_dir, subject_output_dir, folder_maps, folder_ctx, folder_sctx, folder_hip, subject_surf_dir, subject_hippunfold_dir, script_dir, BIDS_ID, VERBOSE, fwhm=None, resolutions=None, labels=None):
    if structure != "subcortex":
        if fwhm is None:
            raise ValueError("Error: --fwhm is required when --struct is not 'subcortex'")
        if resolutions is None:
            raise ValueError("Error: --resolution is required when --struct is not 'subcortex'")
        if labels is None:
            raise ValueError("Error: --labels is required when --struct is not 'subcortex'")

    start_time = time.time()


    # Define mapping functions
    map_struct = {"cortex": "Cortical", "subcortex": "Subcortical", "hippocampus": "Hippocampal"}

    show_title(f"{map_struct[structure]} feature mapping: {BIDS_ID}")
    
    # Perform the mapping

    # thickness -> volume
    if structure == "subcortex":
        features = [feat.replace('thickness', 'volume') for feat in features]

    # do the mapping
    for feat in features:
        if structure == "cortex":
            for res in resolutions:
                for lab in labels:
                    map_cortex(BIDS_ID, feat, res, lab, fwhm, WORKBENCH_PATH, subject_micapipe_dir, subject_output_dir, folder_maps, folder_ctx)
        elif structure == "subcortex":
            map_subcortex(BIDS_ID, feat, subject_surf_dir, subject_micapipe_dir, subject_output_dir, folder_maps, folder_sctx, script_dir)
        elif structure == "hippocampus":
            for res in resolutions:
                for lab in labels:
                    map_hippocampus(BIDS_ID, feat, res, lab, WORKBENCH_PATH, subject_hippunfold_dir, subject_micapipe_dir, subject_output_dir, folder_maps, folder_hip, fwhm)

    # Wrap up
    elapsed = round((time.time() - start_time)/60, 2)
    print(f"{map_struct[structure]} feature mapping for {BIDS_ID} ended in {elapsed} minutes")