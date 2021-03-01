from classes.min_phase_converter import min_phase_converter

#SOFA_filename = '../../HRTF_data/SOFA_MIT/mit_kemar_normal_pinna.sofa'
SOFA_filename = '../../HRTF_data/HUTUBS//HRIRs/pp1_HRIRs_measured.sofa'

min_phase_converter_class = min_phase_converter(SOFA_filename)
min_phase_converter_class.convert_HRIR()


