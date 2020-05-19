import sys
sys.path.insert(0, "..")
import logging

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()

from opcua import ua, Server

import EpeverChargeController as cc


DUMMY_DATA = True


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger = logging.getLogger("opcua.server.internal_subscription")
    logger.setLevel(logging.DEBUG)

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()

    # populating our address space
    epeverObject = objects.add_object(idx, "EpeverObject")

    # creating my machinery objects
    chargeController = cc.EpeverChargeController(produce_dummy_data = DUMMY_DATA)

    ### Creating a custom event: Approach 1
    # The custom event object automatically will have members from its parent (BaseEventType)
    eventType = server.create_custom_event_type(
                    idx,
                    'ChargeControllerDataEvent',
                    ua.ObjectIds.BaseEventType,
                    [
                        ('panelVoltage',       ua.VariantType.Float),
                        ('panelCurrent',       ua.VariantType.Float),
                        ('batteryVoltage',     ua.VariantType.Float),
                        ('batteryCurrent',     ua.VariantType.Float),
                        ('loadVoltage',        ua.VariantType.Float),
                        ('loadCurrent',        ua.VariantType.Float),
                        ('inPower',            ua.VariantType.Float),
                        ('outPower',           ua.VariantType.Float),
                        ('batteryStatus',      ua.VariantType.String),
                        ('batteryTemperature', ua.VariantType.Float),
                        ('batteryCapacity',    ua.VariantType.Float),
                    ]
                )

    myEventGenerator = server.get_event_generator(eventType, epeverObject)

'''
    ### Creating a custom event: Approach 2
    custom_etype = server.nodes.base_event_type.add_object_type(2, 'MySecondEvent')
    custom_etype.add_property(2, 'MyIntProperty' , ua.Variant(0   , ua.VariantType.Int32   ))
    custom_etype.add_property(2, 'MyBoolProperty', ua.Variant(True, ua.VariantType.Boolean ))

    mysecondevgen = server.get_event_generator(custom_etype, myobj)
'''

    # starting!
    server.start()

    try:
        # time.sleep is here just because we want to see events in UaExpert
        import time
        count = 0
        while True:
            time.sleep(1)
            data = chargeController.readAllData()
            myEventGenerator.event.Message           = ua.LocalizedText("ChargeControllerDataEvent %d" % count)
            myEventGenerator.event.Severity          = count

            myEventGenerator.event.panelVoltage       = data['panelVoltage']
            myEventGenerator.event.panelCurrent       = data['panelCurrent']
            myEventGenerator.event.batteryVoltage     = data['batteryVoltage']
            myEventGenerator.event.batteryCurrent     = data['batteryCurrent']
            myEventGenerator.event.loadVoltage        = data['loadVoltage']
            myEventGenerator.event.loadCurrent        = data['loadCurrent']
            myEventGenerator.event.inPower            = data['inPower']
            myEventGenerator.event.outPower           = data['outPower']
            myEventGenerator.event.batteryStatus      = data['batteryStatus']
            myEventGenerator.event.batteryCapacity    = data['batteryCapacity']
            myEventGenerator.event.batteryTemperature = data['batteryTemperature']

            myEventGenerator.trigger()
            #mysecondevgen.trigger(message="MySecondEvent %d" % count)
            count += 1

        embed()
    finally:
        # close connection, remove subcsriptions, etc
        server.stop()
