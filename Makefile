# Makefile for the openflexure microscope
# Generated by generate_makefile.py
.PHONY: all cleanstl

SOURCE = openscad
OUTPUT = builds

body_versions = LS65 LS65-M LS75 LS75-M
optics_versions = picamera_2_pilens_LS65 logitech_c270_c270_lens_LS65 picamera_2_rms_f40d16_LS65 picamera_2_rms_f50d13_LS65 logitech_c270_rms_f40d16_LS65 logitech_c270_rms_f50d13_LS65 m12_rms_f40d16_LS65 m12_rms_f50d13_LS65 m12_m12_lens_LS65
sample_riser_versions = LS10 LS5 SS5
slide_riser_versions = LS10

TOOLS := actuator_assembly_tools condenser_lens_tool tube_lens_tool
TOOLS := $(TOOLS) picamera_2_cover picamera_2_gripper picamera_2_lens_gripper
ACCESSORIES := picamera_2_cover $(sample_riser_versions:%=sample_riser_%) $(slide_riser_versions:%=slide_riser_%) microscope_stand motor_driver_case
COMMONPARTS := feet feet_tall gears sample_clips small_gears
BODIES := $(body_versions:%=main_body_%)
OPTICS := $(optics_versions:%=optics_%) camera_platform_picamera_2_LS65 lens_spacer_picamera_2_pilens_LS65
ILLUMINATIONS := illumination_dovetail condenser
ALLPARTS := $(COMMONPARTS) $(TOOLS) $(BODIES) $(ILLUMINATIONS) $(OPTICS) $(ACCESSORIES)
ALLSTLFILES := $(ALLPARTS:%=$(OUTPUT)/%.stl)

parameters_file := $(SOURCE)/microscope_parameters.scad
utilities_file := $(SOURCE)/utilities.scad
all_deps := $(parameters_file) $(utilities_file) 			#All targets depend on these

all: $(ALLSTLFILES)

cleanstl:
	rm $(STLFILES)

#parameter and utilities files affect everything
$(OUTPUT)/%.stl: $(all_deps)

main_body_dep_names := compact_nut_seat dovetail logo z_axis
main_body_deps := $(main_body_dep_names:%=$(SOURCE)/%.scad)
$(OUTPUT)/main_body_LS65.stl: $(SOURCE)/main_body.scad $(main_body_deps)
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/main_body_LS65-M.stl: $(SOURCE)/main_body.scad $(main_body_deps)
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=true' $<

$(OUTPUT)/main_body_LS75.stl: $(SOURCE)/main_body.scad $(main_body_deps)
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=75' -D 'motor_lugs=false' $<

$(OUTPUT)/main_body_LS75-M.stl: $(SOURCE)/main_body.scad $(main_body_deps)
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=75' -D 'motor_lugs=true' $<


$(OUTPUT)/illumination_dovetail_LS65.stl: $(SOURCE)/illumination_dovetail.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/condenser_LS65.stl: $(SOURCE)/condenser.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/illumination_dovetail_LS65-M.stl: $(SOURCE)/illumination_dovetail.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=true' $<

$(OUTPUT)/condenser_LS65-M.stl: $(SOURCE)/condenser.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=true' $<

$(OUTPUT)/illumination_dovetail_LS75.stl: $(SOURCE)/illumination_dovetail.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=75' -D 'motor_lugs=false' $<

$(OUTPUT)/condenser_LS75.stl: $(SOURCE)/condenser.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=75' -D 'motor_lugs=false' $<

$(OUTPUT)/illumination_dovetail_LS75-M.stl: $(SOURCE)/illumination_dovetail.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=75' -D 'motor_lugs=true' $<

$(OUTPUT)/condenser_LS75-M.stl: $(SOURCE)/condenser.scad $(main_body_deps) $(SOURCE)/illumination.scad
	openscad -o $@ -D 'big_stage=true' -D 'sample_z=75' -D 'motor_lugs=true' $<


optics_dep_names := dovetail cameras/camera
optics_deps := $(optics_dep_names:%=$(SOURCE)/%.scad)
$(OUTPUT)/optics_picamera_2_pilens_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="pilens"' -D 'camera="picamera_2"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_logitech_c270_c270_lens_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="c270_lens"' -D 'camera="logitech_c270"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_picamera_2_rms_f40d16_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="rms_f40d16"' -D 'camera="picamera_2"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_picamera_2_rms_f50d13_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="rms_f50d13"' -D 'camera="picamera_2"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_logitech_c270_rms_f40d16_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="rms_f40d16"' -D 'camera="logitech_c270"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_logitech_c270_rms_f50d13_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="rms_f50d13"' -D 'camera="logitech_c270"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_m12_rms_f40d16_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="rms_f40d16"' -D 'camera="m12"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_m12_rms_f50d13_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="rms_f50d13"' -D 'camera="m12"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/optics_m12_m12_lens_LS65.stl: $(SOURCE)/optics.scad $(optics_deps)
	openscad -o $@ -D 'optics="m12_lens"' -D 'camera="m12"' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<


$(OUTPUT)/camera_platform_picamera_2_LS65.stl: $(SOURCE)/camera_platform_picamera_2_LS65.scad $(optics_deps)
	openscad -o $@ -D 'big_stage=true' -D 'camera="picamera_2"' -D 'optics="pilens"' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/lens_spacer_picamera_2_pilens_LS65.stl: $(SOURCE)/lens_spacer_picamera_2_pilens_LS65.scad $(optics_deps)
	openscad -o $@ -D 'big_stage=true' -D 'camera="picamera_2"' -D 'optics="pilens"' -D 'sample_z=65' -D 'motor_lugs=false' $<

riser_dep_names := main_body
riser_deps := $(optics_dep_names:%=$(SOURCE)/%.scad)
$(OUTPUT)/sample_riser_LS10.stl: $(SOURCE)/sample_riser.scad $(riser_deps)
	openscad -o $@ -D 'h=10' -D 'big_stage=true' $<

$(OUTPUT)/sample_riser_LS5.stl: $(SOURCE)/sample_riser.scad $(riser_deps)
	openscad -o $@ -D 'h=5' -D 'big_stage=true' $<

$(OUTPUT)/sample_riser_SS5.stl: $(SOURCE)/sample_riser.scad $(riser_deps)
	openscad -o $@ -D 'h=5' -D 'big_stage=false' $<

$(OUTPUT)/slide_riser_LS10.stl: $(SOURCE)/slide_riser.scad $(riser_deps)
	openscad -o $@ -D 'h=10' -D 'big_stage=true' $<


stand_dep_names := main_body
stand_deps := $(optics_dep_names:%=$(SOURCE)/%.scad)
$(OUTPUT)/microscope_stand_LS65-20.stl: $(SOURCE)/microscope_stand.scad $(stand_deps)
	openscad -o $@ -D 'h=20' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<

$(OUTPUT)/microscope_stand_LS65-160.stl: $(SOURCE)/microscope_stand.scad $(stand_deps)
	openscad -o $@ -D 'h=160' -D 'big_stage=true' -D 'sample_z=65' -D 'motor_lugs=false' $<


$(OUTPUT)/picamera_2_%.stl: $(SOURCE)/cameras/picamera_2_%.scad $(all_deps)
	openscad -o $@ -D 'camera="picamera_2"' $<


$(OUTPUT)/feet_tall.stl: $(SOURCE)/feet.scad $(all_deps)
	openscad -o $@ -D 'foot_height=26' $<


$(OUTPUT)/actuator_assembly_tools.stl: $(SOURCE)/actuator_assembly_tools.scad $(all_deps)
	openscad -o $@ -D 'foot_height=26' $<


$(OUTPUT)/%.stl: $(SOURCE)/%.scad $(all_deps)
	openscad -o $@ $<


