# pre-defined extensions

# RV32IMA := opcodes-rv32i opcodes-rv32m opcodes-rv32a opcodes-system

# XPULPIMG
# Branching
RV32XPULPIMG := opcodes-xpulpbr_CUSTOM 
RV32XPULPIMG += opcodes-xpulphwloop_CUSTOM

# Comparison
RV32XPULPIMG += opcodes-xpulpslet_CUSTOM

# Bit Twiddle
RV32XPULPIMG += opcodes-xpulpbitop_CUSTOM
RV32XPULPIMG += opcodes-xpulbitrev_CUSTOM
# RV32XPULPIMG += opcodes-xpulpbitopsmall_CUSTOM #is a subset of opcodes-xpulpbitop_CUSTOM

# Load/Store
# RV32XPULPIMG += opcodes-xpulppostmod_CUSTOM #conflict with opcodes-ssr_CUSTOM

# Arithmetic
RV32XPULPIMG += opcodes-xpulpabs_CUSTOM
RV32XPULPIMG += opcodes-xpulpclip_CUSTOM
RV32XPULPIMG += opcodes-xpulpminmax_CUSTOM
RV32XPULPIMG += opcodes-xpulpmacsi_CUSTOM
RV32XPULPIMG += opcodes-xpulppartmac_CUSTOM # subset of xpulpmacrnhi (declared as pseudo instructions)

# Arithmetic with round and norm
RV32XPULPIMG += opcodes-xpulpaddsubrn_CUSTOM
RV32XPULPIMG += opcodes-xpulpmulrnhi_CUSTOM
RV32XPULPIMG += opcodes-xpulpmacrnhi_CUSTOM

# Packed SIMD
RV32XPULPIMG += opcodes-xpulpvect_CUSTOM
RV32XPULPIMG += opcodes-xpulpvectcomplex_CUSTOM
RV32XPULPIMG += opcodes-xpulpvectshufflepack_CUSTOM


# Snitch
SNITCH_OPCODES := opcodes-dma_CUSTOM opcodes-frep_CUSTOM opcodes-ssr_CUSTOM

# default configurations
MEMPOOL_ISA := opcodes-frep_CUSTOM $(RV32XPULPIMG) opcodes-xpulppostmod_CUSTOM opcodes-rv32d-zfh_DRAFT opcodes-rv32q-zfh_DRAFT opcodes-rv32zfh_DRAFT opcodes-rv64zfh_DRAFT opcodes-sflt_CUSTOM
SNITCH_ISA := $(RV32XPULPIMG) $(SNITCH_OPCODES) opcodes-sflt_CUSTOM
