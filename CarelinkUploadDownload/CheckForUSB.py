import sys
import usb.core

# Put the following lines in your bash_profile (NO! NOW IT IS INSTALLED in /usr/local/lib!):
# export PYTHONPATH=$PYTHONPATH:$HOME/pyusb-1.0.0rc1
# export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$HOME/libusb/lib

def CheckForUSB() :
 
    found = False

    var_usb_device = usb.core.find(find_all = True)

    for var_dev in var_usb_device:
        var_usb = usb.core.find(idVendor=var_dev.idVendor, idProduct=var_dev.idProduct)

        if not getattr(var_usb,'langids') :
            continue

        var_manu    = usb.util.get_string(var_usb,var_usb.iManufacturer,langid=getattr(var_usb,'langids')[0])

        if 'Bayer HealthCare LLC' not in var_manu :
            continue

        found = True

        if True :
            continue

        var_product = usb.util.get_string(var_usb,var_dev.iProduct     ,langid=getattr(var_usb,'langids')[0])
        var_serial  = usb.util.get_string(var_usb,var_dev.iSerialNumber,langid=getattr(var_usb,'langids')[0])
        var_drv     = var_usb.is_kernel_driver_active(0)
        var_cfg     = var_usb.get_active_configuration()
        var_int     = var_cfg[(0,0)].bInterfaceNumber

        print "iManufacturer: ", var_dev.iManufacturer, hex(var_dev.iManufacturer)
        print "IdVendor: ", var_dev.idVendor, hex(var_dev.idVendor)
        print "IdProduct: ", var_dev.idProduct, hex(var_dev.idProduct)
        print "Manufacturer: ", var_manu
        print "Product: ", var_product
        print "Serial: ", var_serial
        print "Interface #: ", var_int
        print "Kernel Driver: ", var_drv

        for var_config in var_usb:
            for var_i in var_config:
                for var_e in var_i:
                    print " - Endpoint Address: ", var_e.bEndpointAddress

    return found

