import sys
sys.path.insert(0, "..")
import logging
import time
import random
from opcua import ua, Server, uamethod
import EpeverChargeController as cc

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


DUMMY_DATA = True
LOW_BATTERY_VOLTAGE = 10.0


## OPC methods definition 1
# method to be exposed through server
def set_plug_state(parent, variant):
    ret = False
    if variant.Value % 2 == 0:
        ret = True
    return [ua.Variant(ret, ua.VariantType.Boolean)]


# method to be exposed through server
# uses a decorator to automatically convert to and from variants
@uamethod
def set_inverter_state(parent, x, y):
    print("multiply method call with parameters: ", x, y)
    return x * y



def main():
    logging.basicConfig(level=logging.WARN)
    logger = logging.getLogger("opcua.server.internal_subscription")
    logger.setLevel(logging.DEBUG)

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    server_namespace = "http://examples.freeopcua.github.io"
    address_space = server.register_namespace( server_namespace )

    # get Objects node, this is where we should put our custom stuff
    objects_node = server.get_objects_node()

    # populating our address space
    ChargeControllerObject = objects_node.add_object(address_space, "ChargeController")
    RelayBoxObject         = objects_node.add_object(address_space, "RelayBox")

    panelVoltage       = ChargeControllerObject.add_variable( address_space, "panelVoltage", 0.0 )
    panelCurrent       = ChargeControllerObject.add_variable( address_space, "panelCurrent", 0.0 )
    batteryVoltage     = ChargeControllerObject.add_variable( address_space, "batteryVoltage", 0.0 )
    batteryCurrent     = ChargeControllerObject.add_variable( address_space, "batteryCurrent", 0.0 )
    loadVoltage        = ChargeControllerObject.add_variable( address_space, "loadVoltage", 0.0 )
    loadCurrent        = ChargeControllerObject.add_variable( address_space, "loadCurrent", 0.0 )
    inPower            = ChargeControllerObject.add_variable( address_space, "inPower", 0.0 )
    outPower           = ChargeControllerObject.add_variable( address_space, "outPower", 0.0 )
    batteryStatus      = ChargeControllerObject.add_variable( address_space, "batteryStatus", "" )
    batteryCapacity    = ChargeControllerObject.add_variable( address_space, "batteryCapacity", 0.0 )
    batteryTemperature = ChargeControllerObject.add_variable( address_space, "batteryTemperature", 0.0 )

    ## To make them writable by the clients
    """
    panelVoltage.set_writable()
    panelCurrent.set_writable()
    batteryCurrent.set_writable()
    batteryVoltage.set_writable()
    loadVoltage.set_writable()
    loadCurrent.set_writable()
    inPower.set_writable()
    outPower.set_writable()
    batteryStatus.set_writable()
    batteryCapacity.set_writable()
    batteryTemperature.set_writable()
    """

    ### Creating a custom EVENT
    eventType = server.create_custom_event_type(
                    address_space,
                    'LowBatteryEvent',
                    ua.ObjectIds.BaseEventType,
                    [
                        ('batteryVoltage', ua.VariantType.Float),
                        ('outputsEnabled', ua.VariantType.Boolean),
                    ]
                )
    myEventGenerator = server.get_event_generator(eventType, ChargeControllerObject)

    ##creating an array
    plug_A_current_array = ChargeControllerObject.add_variable(address_space, "plug_A_current_array", [6.7, 7.9])
    # the variable could be hard typed
    plug_B_current_array = ChargeControllerObject.add_variable(address_space, "plug_B_current_array", ua.Variant([], ua.VariantType.Float))

    ## creating a property
    prop_charge_controller_producer = ChargeControllerObject.add_property(address_space, "charge_controller_producer", "Epever")
    prop_charge_controller_model    = ChargeControllerObject.add_property(address_space, "charge_controller_model", "Tracer 2210A MPPT")
    prop_panel                      = ChargeControllerObject.add_property(address_space, "panel_info",   "12V 100 W")
    prop_battery                    = ChargeControllerObject.add_property(address_space, "battery_info", "Bosch 12V")

    ## Two different methods definitions
    # First
    plugs_control_node = RelayBoxObject.add_method(address_space, "set_plug_state", set_plug_state, [ua.VariantType.Boolean], [ua.VariantType.Boolean])

    # Second
    inarg = ua.Argument()
    inarg.Name = "inverter_state"
    inarg.DataType = ua.NodeId(ua.ObjectIds.Boolean)
    inarg.ValueRank = -1
    inarg.ArrayDimensions = []
    inarg.Description = ua.LocalizedText("Boolean inverter state")
    outarg = ua.Argument()
    outarg.Name = "Result"
    outarg.DataType = ua.NodeId(ua.ObjectIds.Boolean)
    outarg.ValueRank = -1
    outarg.ArrayDimensions = []
    outarg.Description = ua.LocalizedText("Final Inverter State")

    inverter_control_node = RelayBoxObject.add_method(address_space, "set_inverter_state", set_inverter_state, [inarg], [outarg])


    # starting!
    server.start()
    print( "Server starting ...")

    # creating my machinery objects
    chargeController = cc.EpeverChargeController(produce_dummy_data = DUMMY_DATA)
    outputsEnabled = True

    try:

        while True:
            time.sleep(1)
            data = chargeController.readAllData()

            panelVoltage.set_value( data['panelVoltage'] )
            panelCurrent.set_value( data['panelCurrent'] )
            batteryVoltage.set_value( data['batteryVoltage'] )
            batteryCurrent.set_value( data['batteryCurrent'] )
            loadVoltage.set_value( data['loadVoltage'] )
            loadCurrent.set_value( data['loadCurrent'] )
            inPower.set_value( data['inPower'] )
            outPower.set_value( data['outPower'] )
            batteryStatus.set_value( data['batteryStatus'] )
            batteryCapacity.set_value( data['batteryCapacity'] )
            batteryTemperature.set_value( data['batteryTemperature'] )

            if data['batteryVoltage'] < LOW_BATTERY_VOLTAGE and outputsEnabled:
                outputsEnabled = False;
                myEventGenerator.event.Message = ua.LocalizedText("Battery Voltage is too low. Outputs will be disconnected")
                myEventGenerator.event.batteryVoltage =  ua.Variant(float(data['panelVoltage']), ua.VariantType.Float)
                myEventGenerator.event.outputsEnabled =  ua.Variant( outputsEnabled , ua.VariantType.Boolean)
                myEventGenerator.event.Severity =  ua.Variant( 1 , ua.VariantType.Int32)
                myEventGenerator.trigger()
            elif data['batteryVoltage'] > LOW_BATTERY_VOLTAGE and not outputsEnabled:
                outputsEnabled = True;
                myEventGenerator.event.Message = ua.LocalizedText("Battery Voltage is normal. Outputs will be activated")
                myEventGenerator.event.batteryVoltage =  ua.Variant(float(data['panelVoltage']), ua.VariantType.Float)
                myEventGenerator.event.outputsEnabled =  ua.Variant( outputsEnabled , ua.VariantType.Boolean)
                myEventGenerator.event.Severity =  ua.Variant( 1 , ua.VariantType.Int32)
                myEventGenerator.trigger()

            ## update array variables
            burst = [random.random() for _ in range(1024)]
            plug_A_current_array.set_value(burst)
            plug_B_current_array.set_value(burst)

        embed()
    finally:
        # close connection, remove subcsriptions, etc
        server.stop()



if __name__ == "__main__":
    main()
