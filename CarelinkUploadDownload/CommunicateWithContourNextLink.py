import sys
import usb.core

# Put the following lines in your bash_profile (NO! NOW IT IS INSTALLED in /usr/local/lib!):
# export PYTHONPATH=$PYTHONPATH:$HOME/pyusb-1.0.0rc1
# export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$HOME/libusb/lib

def main(options,args) :
 
    device = usb.core.find(idVendor=0x1a79, idProduct=0x6200)
    print device

    var_product = usb.util.get_string(device,device.iProduct     ,langid=getattr(device,'langids')[0])
    var_serial  = usb.util.get_string(device,device.iSerialNumber,langid=getattr(device,'langids')[0])
    var_drv     = device.is_kernel_driver_active(0)
    var_cfg     = device.get_active_configuration()
    var_int     = var_cfg[(0,0)].bInterfaceNumber

    print "iManufacturer: ", device.iManufacturer, hex(device.iManufacturer)
    print "IdVendor: ", device.idVendor, hex(device.idVendor)
    print "IdProduct: ", device.idProduct, hex(device.idProduct)

    ## one of the first things you need to do before communicating with it is
    ## issuing a ``set_configuration`` request
    device.set_configuration(0x1)

    print device.is_kernel_driver_active(0x0)
    device.detach_kernel_driver(0x0)
    ret = device.read(0x1, 0x40, 100) # endpoint, size_or_buffer, timeout
    #print ret

    return True

#-----------------------------------------------
if __name__ == '__main__':
    main(None,None)
