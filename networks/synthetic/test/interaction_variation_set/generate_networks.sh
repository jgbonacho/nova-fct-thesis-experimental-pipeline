# 14_nM_uM_onnL_omM (mu(M) x om(M))
../../synthetic_networks_lfr_generator.sh \
  'network_family_name="14_nM_uM_onnL_omM"' \
  'list_n=(1000)' \
  'list_mu=(0.4 0.5 0.6)' \
  'list_on_percentages=(20)' \
  'list_om=(4 5)' \
  't=5'

# 15_nM_uM_onnM_omL (mu(M) x on(M))
../../synthetic_networks_lfr_generator.sh \
  'network_family_name="15_nM_uM_onnM_omL"' \
  'list_n=(1000)' \
  'list_mu=(0.4 0.5 0.6)' \
  'list_on_percentages=(30 40)' \
  'list_om=(2)' \
  't=5'

# 16_nM_uM_onnM_omM (om(M) x on(M))
../../synthetic_networks_lfr_generator.sh \
  'network_family_name="16_nM_uM_onnM_omM"' \
  'list_n=(1000)' \
  'list_mu=(0.4)' \
  'list_on_percentages=(30 40)' \
  'list_om=(4 5)' \
  't=5'
