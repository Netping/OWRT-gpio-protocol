SECTION="NetPing modules"
CATEGORY="Base"
TITLE="EPIC12 OWRT_GPIO_Protocol"

PKG_NAME="OWRT_GPIO_Protocol"
PKG_VERSION="Epic12.V1.S1"
PKG_RELEASE=1

CONF_FILE=gpioconf
CONF_DIR=/etc/config/

MODULE_FILES=gpioproto.py
MODULE_FILES_DIR=/usr/lib/python3.7/

ETC_FILES=
ETC_FILES_DIR=/etc/netping_gpio/


.PHONY: all install

all: install
	
install:
	cp $(CONF_FILE) $(CONF_DIR)
	for f in $(MODULE_FILES); do cp $${f} $(MODULE_FILES_DIR); done
	mkdir $(ETC_FILES_DIR)
	for f in $(ETC_FILES); do cp etc/$${f} $(ETC_FILES_DIR); done

clean:
	rm -f $(CONF_DIR)$(CONF_FILE)
	for f in $(MODULE_FILES); do rm -f $(MODULE_FILES_DIR)$${f}; done
	rm -rf $(ETC_FILES_DIR)
