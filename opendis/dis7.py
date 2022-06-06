#
# This code is licensed under the BSD software license
#

def null():
    return None


class DataQueryDatumSpecification(object):
    """List of fixed and variable datum records. Section 6.2.17 """

    def __init__(self):
        """ Initializer for DataQueryDatumSpecification"""
        self.numberOfFixedDatums = 0
        """ Number of fixed datums"""
        self.numberOfVariableDatums = 0
        """ Number of variable datums"""
        self.fixedDatumIDList = []
        """ variable length list fixed datum IDs"""
        self.variableDatumIDList = []
        """ variable length list variable datum IDs"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(len(self.fixedDatumIDList))
        output_stream.write_unsigned_int(len(self.variableDatumIDList))
        for anObj in self.fixedDatumIDList:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumIDList:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.numberOfFixedDatums = input_stream.read_unsigned_int()
        self.numberOfVariableDatums = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatums):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumIDList.append(element)

        for idx in range(0, self.numberOfVariableDatums):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumIDList.append(element)


class RadioIdentifier(object):
    """The unique designation of an attached or unattached radio in an event or exercise Section 6.2.70"""

    def __init__(self):
        """ Initializer for RadioIdentifier"""
        self.siteNumber = 0
        """  site"""
        self.applicationNumber = 0
        """ application number"""
        self.referenceNumber = 0
        """  reference number"""
        self.radioNumber = 0
        """  Radio number"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.siteNumber)
        output_stream.write_unsigned_short(self.applicationNumber)
        output_stream.write_unsigned_short(self.referenceNumber)
        output_stream.write_unsigned_short(self.radioNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.siteNumber = input_stream.read_unsigned_short()
        self.applicationNumber = input_stream.read_unsigned_short()
        self.referenceNumber = input_stream.read_unsigned_short()
        self.radioNumber = input_stream.read_unsigned_short()


class RequestID(object):
    """A monotonically increasing number inserted into all simulation managment PDUs. This should be a hand-coded thingie, maybe a singleton. Section 6.2.75"""

    def __init__(self):
        """ Initializer for RequestID"""
        self.requestID = 0
        """ monotonically increasing number"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.requestID = input_stream.read_unsigned_int()


class IFFData(object):
    """repeating element if IFF Data specification record"""

    def __init__(self):
        """ Initializer for IFFData"""
        self.recordType = 0
        """ enumeration for type of record"""
        self.recordLength = 0
        """ length of record. Should be padded to 32 bit boundary."""
        self.iffData = []
        """ IFF data."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(len(self.iffData))
        for anObj in self.iffData:
            output_stream.write_unsigned_byte(anObj)

        """ TODO add padding to end on 32-bit boundary """

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        """ The record length includes the length of record type field (32 bits) and record length field (16 bits) so we subtract 6 bytes total for those. """
        for idx in range(0, self.recordLength - 6):
            val = input_stream.read_unsigned_byte()
            self.iffData.append(val)


class MunitionDescriptor(object):
    """Represents the firing or detonation of a munition. Section 6.2.19.2"""

    def __init__(self):
        """ Initializer for MunitionDescriptor"""
        self.munitionType = EntityType()
        """ What munition was used in the burst"""
        self.warhead = 0
        """ type of warhead enumeration"""
        self.fuse = 0
        """ type of fuse used enumeration"""
        self.quantity = 0
        """ how many of the munition were fired"""
        self.rate = 0
        """ rate at which the munition was fired"""

    def serialize(self, output_stream):
        """serialize the class """
        self.munitionType.serialize(output_stream)
        output_stream.write_unsigned_short(self.warhead)
        output_stream.write_unsigned_short(self.fuse)
        output_stream.write_unsigned_short(self.quantity)
        output_stream.write_unsigned_short(self.rate)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.munitionType.parse(input_stream)
        self.warhead = input_stream.read_unsigned_short()
        self.fuse = input_stream.read_unsigned_short()
        self.quantity = input_stream.read_unsigned_short()
        self.rate = input_stream.read_unsigned_short()


class MinefieldSensorType(object):
    """Information about a minefield sensor. Section 6.2.57"""

    def __init__(self):
        """ Initializer for MinefieldSensorType"""
        self.sensorType = 0
        """ sensor type. bit fields 0-3 are the type category, 4-15 are teh subcategory"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.sensorType)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.sensorType = input_stream.read_unsigned_short()


class GroupID(object):
    """Unique designation of a group of entities contained in the isGroupOfPdu. Represents a group of entities rather than a single entity. Section 6.2.43"""

    def __init__(self):
        """ Initializer for GroupID"""
        self.simulationAddress = EntityType()
        """ Simulation address (site and application number)"""
        self.groupNumber = 0
        """ group number"""

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.groupNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.groupNumber = input_stream.read_unsigned_short()


class LayerHeader(object):
    """The identification of the additional information layer number, layer-specific information, and the length of the layer. Section 6.2.51"""

    def __init__(self):
        """ Initializer for LayerHeader"""
        self.layerNumber = 0
        self.layerSpecificInformation = 0
        """ field shall specify layer-specific information that varies by System Type (see 6.2.86) and Layer Number."""
        self.length = 0
        """ This field shall specify the length in octets of the layer, including the Layer Header record"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.layerNumber)
        output_stream.write_unsigned_byte(self.layerSpecificInformation)
        output_stream.write_unsigned_short(self.length)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.layerNumber = input_stream.read_unsigned_byte()
        self.layerSpecificInformation = input_stream.read_unsigned_byte()
        self.length = input_stream.read_unsigned_short()


class UnsignedDISInteger(object):
    """container class not in specification"""

    def __init__(self):
        """ Initializer for UnsignedDISInteger"""
        self.val = 0
        """ unsigned integer"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.val)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.val = input_stream.read_unsigned_int()


class DeadReckoningParameters(object):
    """Not specified in the standard. This is used by the ESPDU"""

    def __init__(self):
        """ Initializer for DeadReckoningParameters"""
        self.deadReckoningAlgorithm = 0
        """ Algorithm to use in computing dead reckoning. See EBV doc."""
        self.parameters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        """ Dead reckoning parameters. Contents depends on algorithm."""
        self.entityLinearAcceleration = Vector3Float()
        """ Linear acceleration of the entity"""
        self.entityAngularVelocity = Vector3Float()
        """ Angular velocity of the entity"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.deadReckoningAlgorithm)
        for idx in range(0, 15):
            output_stream.write_unsigned_byte(self.parameters[idx])

        self.entityLinearAcceleration.serialize(output_stream)
        self.entityAngularVelocity.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.deadReckoningAlgorithm = input_stream.read_unsigned_byte()
        self.parameters = [0] * 15
        for idx in range(0, 15):
            val = input_stream.read_unsigned_byte()

            self.parameters[idx] = val

        self.entityLinearAcceleration.parse(input_stream)
        self.entityAngularVelocity.parse(input_stream)


class ProtocolMode(object):
    """Bit field used to identify minefield data. bits 14-15 are a 2-bit enum, other bits unused. Section 6.2.69"""

    def __init__(self):
        """ Initializer for ProtocolMode"""
        self.protocolMode = 0
        """ Bitfields, 14-15 contain an enum"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.protocolMode)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.protocolMode = input_stream.read_unsigned_short()


class AngleDeception(object):
    """The Angle Deception attribute record may be used to communicate discrete values that are associated with angle deception jamming that cannot be referenced to an emitter mode. The values provided in the record records (provided in the associated Electromagnetic Emission PDU). (The victim radar beams are those that are targeted by the jammer.) Section 6.2.21.2.2"""

    def __init__(self):
        """ Initializer for AngleDeception"""
        self.recordType = 3501
        self.recordLength = 48
        self.padding = 0
        self.emitterNumber = 0
        self.beamNumber = 0
        self.stateIndicator = 0
        self.padding2 = 0
        self.azimuthOffset = 0
        self.azimuthWidth = 0
        self.azimuthPullRate = 0
        self.azimuthPullAcceleration = 0
        self.elevationOffset = 0
        self.elevationWidth = 0
        self.elevationPullRate = 0
        self.elevationPullAcceleration = 0
        self.padding3 = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_short(self.padding)
        output_stream.write_unsigned_byte(self.emitterNumber)
        output_stream.write_unsigned_byte(self.beamNumber)
        output_stream.write_unsigned_byte(self.stateIndicator)
        output_stream.write_unsigned_byte(self.padding2)
        output_stream.write_float(self.azimuthOffset)
        output_stream.write_float(self.azimuthWidth)
        output_stream.write_float(self.azimuthPullRate)
        output_stream.write_float(self.azimuthPullAcceleration)
        output_stream.write_float(self.elevationOffset)
        output_stream.write_float(self.elevationWidth)
        output_stream.write_float(self.elevationPullRate)
        output_stream.write_float(self.elevationPullAcceleration)
        output_stream.write_unsigned_int(self.padding3)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()
        self.emitterNumber = input_stream.read_unsigned_byte()
        self.beamNumber = input_stream.read_unsigned_byte()
        self.stateIndicator = input_stream.read_unsigned_byte()
        self.padding2 = input_stream.read_unsigned_byte()
        self.azimuthOffset = input_stream.read_float()
        self.azimuthWidth = input_stream.read_float()
        self.azimuthPullRate = input_stream.read_float()
        self.azimuthPullAcceleration = input_stream.read_float()
        self.elevationOffset = input_stream.read_float()
        self.elevationWidth = input_stream.read_float()
        self.elevationPullRate = input_stream.read_float()
        self.elevationPullAcceleration = input_stream.read_float()
        self.padding3 = input_stream.read_unsigned_int()


class EntityAssociation(object):
    """Association or disassociation of two entities.  Section 6.2.94.4.3"""

    def __init__(self):
        """ Initializer for EntityAssociation"""
        self.recordType = 4
        """ the identification of the Variable Parameter record. Enumeration from EBV"""
        self.changeIndicator = 0
        """ Indicates if this VP has changed since last issuance"""
        self.associationStatus = 0
        """ Indicates association status between two entities 8 bit enum"""
        self.associationType = 0
        """ Type of association 8 bit enum"""
        self.entityID = EntityID()
        """ Object ID of entity associated with this entity"""
        self.ownStationLocation = 0
        """ Station location on one's own entity. EBV doc."""
        self.physicalConnectionType = 0
        """ Type of physical connection. EBV doc"""
        self.groupMemberType = 0
        """ Type of member the entity is within th egroup"""
        self.groupNumber = 0
        """ Group if any to which the entity belongs"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.recordType)
        output_stream.write_unsigned_byte(self.changeIndicator)
        output_stream.write_unsigned_byte(self.associationStatus)
        output_stream.write_unsigned_byte(self.associationType)
        self.entityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.ownStationLocation)
        output_stream.write_unsigned_byte(self.physicalConnectionType)
        output_stream.write_unsigned_byte(self.groupMemberType)
        output_stream.write_unsigned_short(self.groupNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_byte()
        self.changeIndicator = input_stream.read_unsigned_byte()
        self.associationStatus = input_stream.read_unsigned_byte()
        self.associationType = input_stream.read_unsigned_byte()
        self.entityID.parse(input_stream)
        self.ownStationLocation = input_stream.read_unsigned_short()
        self.physicalConnectionType = input_stream.read_unsigned_byte()
        self.groupMemberType = input_stream.read_unsigned_byte()
        self.groupNumber = input_stream.read_unsigned_short()


class VectoringNozzleSystem(object):
    """Operational data for describing the vectoring nozzle systems Section 6.2.96"""

    def __init__(self):
        """ Initializer for VectoringNozzleSystem"""
        self.horizontalDeflectionAngle = 0
        """ In degrees"""
        self.verticalDeflectionAngle = 0
        """ In degrees"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.horizontalDeflectionAngle)
        output_stream.write_float(self.verticalDeflectionAngle)

    def parse(self, input_stream):
        """Parse a message. This may recursively call embedded objects."""

        self.horizontalDeflectionAngle = input_stream.read_float()
        self.verticalDeflectionAngle = input_stream.read_float()


class FalseTargetsAttribute(object):
    """The False Targets attribute record shall be used to communicate discrete values that are associated with false targets jamming that cannot be referenced to an emitter mode. The values provided in the False Targets attri- bute record shall be considered valid only for the victim radar beams listed in the jamming beam's Track/Jam Data records (provided in the associated Electromagnetic Emission PDU). Section 6.2.21.3"""

    def __init__(self):
        """ Initializer for FalseTargetsAttribute"""
        self.recordType = 3502
        self.recordLength = 40
        self.padding = 0
        self.emitterNumber = 0
        self.beamNumber = 0
        self.stateIndicator = 0
        self.padding2 = 0
        self.falseTargetCount = 0
        self.walkSpeed = 0
        self.walkAcceleration = 0
        self.maximumWalkDistance = 0
        self.keepTime = 0
        self.echoSpacing = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_short(self.padding)
        output_stream.write_unsigned_byte(self.emitterNumber)
        output_stream.write_unsigned_byte(self.beamNumber)
        output_stream.write_unsigned_byte(self.stateIndicator)
        output_stream.write_unsigned_byte(self.padding2)
        output_stream.write_unsigned_short(self.falseTargetCount)
        output_stream.write_float(self.walkSpeed)
        output_stream.write_float(self.walkAcceleration)
        output_stream.write_float(self.maximumWalkDistance)
        output_stream.write_float(self.keepTime)
        output_stream.write_float(self.echoSpacing)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()
        self.emitterNumber = input_stream.read_unsigned_byte()
        self.beamNumber = input_stream.read_unsigned_byte()
        self.stateIndicator = input_stream.read_unsigned_byte()
        self.padding2 = input_stream.read_unsigned_byte()
        self.falseTargetCount = input_stream.read_unsigned_short()
        self.walkSpeed = input_stream.read_float()
        self.walkAcceleration = input_stream.read_float()
        self.maximumWalkDistance = input_stream.read_float()
        self.keepTime = input_stream.read_float()
        self.echoSpacing = input_stream.read_float()


class MinefieldIdentifier(object):
    """The unique designation of a minefield Section 6.2.56 """

    def __init__(self):
        """ Initializer for MinefieldIdentifier"""
        self.simulationAddress = SimulationAddress()
        """ """
        self.minefieldNumber = 0
        """ """

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.minefieldNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.minefieldNumber = input_stream.read_unsigned_short()


class RadioType(object):
    """Identifies the type of radio. Section 6.2.71"""

    def __init__(self):
        """ Initializer for RadioType"""
        self.entityKind = 0
        """ Kind of entity"""
        self.domain = 0
        """ Domain of entity (air, surface, subsurface, space, etc)"""
        self.country = 0
        """ country to which the design of the entity is attributed"""
        self.category = 0
        """ category of entity"""
        self.subcategory = 0
        """ specific info based on subcategory field"""
        self.specific = 0
        self.extra = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.entityKind)
        output_stream.write_unsigned_byte(self.domain)
        output_stream.write_unsigned_short(self.country)
        output_stream.write_unsigned_byte(self.category)
        output_stream.write_unsigned_byte(self.subcategory)
        output_stream.write_unsigned_byte(self.specific)
        output_stream.write_unsigned_byte(self.extra)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.entityKind = input_stream.read_unsigned_byte()
        self.domain = input_stream.read_unsigned_byte()
        self.country = input_stream.read_unsigned_short()
        self.category = input_stream.read_unsigned_byte()
        self.subcategory = input_stream.read_unsigned_byte()
        self.specific = input_stream.read_unsigned_byte()
        self.extra = input_stream.read_unsigned_byte()


class NamedLocationIdentification(object):
    """Information about the discrete positional relationship of the part entity with respect to the its host entity Section 6.2.62 """

    def __init__(self):
        """ Initializer for NamedLocationIdentification"""
        self.stationName = 0
        """ the station name within the host at which the part entity is located. If the part entity is On Station, this field shall specify the representation of the parts location data fields. This field shall be specified by a 16-bit enumeration """
        self.stationNumber = 0
        """ the number of the particular wing station, cargo hold etc., at which the part is attached. """

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.stationName)
        output_stream.write_unsigned_short(self.stationNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.stationName = input_stream.read_unsigned_short()
        self.stationNumber = input_stream.read_unsigned_short()


class FourByteChunk(object):
    """32 bit piece of data"""

    def __init__(self):
        """ Initializer for FourByteChunk"""
        self.otherParameters = [0, 0, 0, 0]
        """ four bytes of arbitrary data"""

    def serialize(self, output_stream):
        """serialize the class """
        for idx in range(0, 4):
            output_stream.write_byte(self.otherParameters[idx])

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.otherParameters = [0] * 4
        for idx in range(0, 4):
            val = input_stream.read_byte()

            self.otherParameters[idx] = val


class ModulationParameters(object):
    """Modulation parameters associated with a specific radio system. INCOMPLETE. 6.2.58 """

    def __init__(self):
        """ Initializer for ModulationParameters"""

    def serialize(self, output_stream):
        """serialize the class """

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""


class OneByteChunk(object):
    """8 bit piece of data"""

    def __init__(self):
        """ Initializer for OneByteChunk"""
        self.otherParameters = [0]
        """ one byte of arbitrary data"""

    def serialize(self, output_stream):
        """serialize the class """
        for idx in range(0, 1):
            output_stream.write_byte(self.otherParameters[idx])

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.otherParameters = [0] * 1
        for idx in range(0, 1):
            val = input_stream.read_byte()

            self.otherParameters[idx] = val


class EulerAngles(object):
    """Three floating point values representing an orientation, psi, theta, and phi, aka the euler angles, in radians. Section 6.2.33"""

    def __init__(self):
        """ Initializer for EulerAngles"""
        self.psi = 0
        self.theta = 0
        self.phi = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.psi)
        output_stream.write_float(self.theta)
        output_stream.write_float(self.phi)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.psi = input_stream.read_float()
        self.theta = input_stream.read_float()
        self.phi = input_stream.read_float()


class DirectedEnergyPrecisionAimpoint(object):
    """DE Precision Aimpoint Record. Section 6.2.20.3"""

    def __init__(self):
        """ Initializer for DirectedEnergyPrecisionAimpoint"""
        self.recordType = 4000
        """ Type of Record"""
        self.recordLength = 88
        """ Length of Record"""
        self.padding = 0
        """ Padding"""
        self.targetSpotLocation = Vector3Double()
        """ Position of Target Spot in World Coordinates."""
        self.targetSpotEntityLocation = Vector3Float()
        """ Position (meters) of Target Spot relative to Entity Position."""
        self.targetSpotVelocity = Vector3Float()
        """ Velocity (meters/sec) of Target Spot."""
        self.targetSpotAcceleration = Vector3Float()
        """ Acceleration (meters/sec/sec) of Target Spot."""
        self.targetEntityID = EntityID()
        """ Unique ID of the target entity."""
        self.targetComponentID = 0
        """ Target Component ID ENUM, same as in DamageDescriptionRecord."""
        self.beamSpotType = 0
        """ Spot Shape ENUM."""
        self.beamSpotCrossSectionSemiMajorAxis = 0
        """ Beam Spot Cross Section Semi-Major Axis."""
        self.beamSpotCrossSectionSemiMinorAxis = 0
        """ Beam Spot Cross Section Semi-Major Axis."""
        self.beamSpotCrossSectionOrientationAngle = 0
        """ Beam Spot Cross Section Orientation Angle."""
        self.peakIrradiance = 0
        """ Peak irradiance"""
        self.padding2 = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_short(self.padding)
        self.targetSpotLocation.serialize(output_stream)
        self.targetSpotEntityLocation.serialize(output_stream)
        self.targetSpotVelocity.serialize(output_stream)
        self.targetSpotAcceleration.serialize(output_stream)
        self.targetEntityID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.targetComponentID)
        output_stream.write_unsigned_byte(self.beamSpotType)
        output_stream.write_float(self.beamSpotCrossSectionSemiMajorAxis)
        output_stream.write_float(self.beamSpotCrossSectionSemiMinorAxis)
        output_stream.write_float(self.beamSpotCrossSectionOrientationAngle)
        output_stream.write_float(self.peakIrradiance)
        output_stream.write_unsigned_int(self.padding2)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()
        self.targetSpotLocation.parse(input_stream)
        self.targetSpotEntityLocation.parse(input_stream)
        self.targetSpotVelocity.parse(input_stream)
        self.targetSpotAcceleration.parse(input_stream)
        self.targetEntityID.parse(input_stream)
        self.targetComponentID = input_stream.read_unsigned_byte()
        self.beamSpotType = input_stream.read_unsigned_byte()
        self.beamSpotCrossSectionSemiMajorAxis = input_stream.read_float()
        self.beamSpotCrossSectionSemiMinorAxis = input_stream.read_float()
        self.beamSpotCrossSectionOrientationAngle = input_stream.read_float()
        self.peakIrradiance = input_stream.read_float()
        self.padding2 = input_stream.read_unsigned_int()


class IffDataSpecification(object):
    """Requires hand coding to be useful. Section 6.2.43"""

    def __init__(self):
        """ Initializer for IffDataSpecification"""
        self.numberOfIffDataRecords = 0
        """ Number of iff records"""
        self.iffDataRecords = []
        """ IFF data records"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(len(self.iffDataRecords))
        for anObj in self.iffDataRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.numberOfIffDataRecords = input_stream.read_unsigned_short()
        for idx in range(0, self.numberOfIffDataRecords):
            element = IFFData()
            element.parse(input_stream)
            self.iffDataRecords.append(element)


class OwnershipStatus(object):
    """used to convey entity and conflict status information associated with transferring ownership of an entity. Section 6.2.65"""

    def __init__(self):
        """ Initializer for OwnershipStatus"""
        self.entityId = EntityID()
        """ EntityID"""
        self.ownershipStatus = 0
        """ The ownership and/or ownership conflict status of the entity represented by the Entity ID field."""
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        self.entityId.serialize(output_stream)
        output_stream.write_unsigned_byte(self.ownershipStatus)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.entityId.parse(input_stream)
        self.ownershipStatus = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class BeamAntennaPattern(object):
    """Used when the antenna pattern type field has a value of 1. Specifies the direction, pattern, and polarization of radiation from an antenna. Section 6.2.9.2"""

    def __init__(self):
        """ Initializer for BeamAntennaPattern"""
        self.beamDirection = EulerAngles()
        """ The rotation that transforms the reference coordinate sytem into the beam coordinate system. Either world coordinates or entity coordinates may be used as the reference coordinate system, as specified by the reference system field of the antenna pattern record."""
        self.azimuthBeamwidth = 0
        self.elevationBeamwidth = 0
        self.referenceSystem = 0
        self.padding1 = 0
        self.padding2 = 0
        self.ez = 0.0
        """ This field shall specify the magnitude of the Z-component (in beam coordinates) of the Electrical field at some arbitrary single point in the main beam and in the far field of the antenna. """
        self.ex = 0.0
        """ This field shall specify the magnitude of the X-component (in beam coordinates) of the Electri- cal field at some arbitrary single point in the main beam and in the far field of the antenna."""
        self.phase = 0.0
        """ This field shall specify the phase angle between EZ and EX in radians. If fully omni-direc- tional antenna is modeled using beam pattern type one, the omni-directional antenna shall be repre- sented by beam direction Euler angles psi, theta, and phi of zero, an azimuth beamwidth of 2PI, and an elevation beamwidth of PI"""
        self.padding3 = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        self.beamDirection.serialize(output_stream)
        output_stream.write_float(self.azimuthBeamwidth)
        output_stream.write_float(self.elevationBeamwidth)
        output_stream.write_unsigned_byte(self.referenceSystem)
        output_stream.write_unsigned_byte(self.padding1)
        output_stream.write_unsigned_short(self.padding2)
        output_stream.write_float(self.ez)
        output_stream.write_float(self.ex)
        output_stream.write_float(self.phase)
        output_stream.write_unsigned_int(self.padding3)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.beamDirection.parse(input_stream)
        self.azimuthBeamwidth = input_stream.read_float()
        self.elevationBeamwidth = input_stream.read_float()
        self.referenceSystem = input_stream.read_unsigned_byte()
        self.padding1 = input_stream.read_unsigned_byte()
        self.padding2 = input_stream.read_unsigned_short()
        self.ez = input_stream.read_float()
        self.ex = input_stream.read_float()
        self.phase = input_stream.read_float()
        self.padding3 = input_stream.read_unsigned_int()


class AttachedParts(object):
    """Removable parts that may be attached to an entity.  Section 6.2.93.3"""

    def __init__(self):
        """ Initializer for AttachedParts"""
        self.recordType = 1
        """ the identification of the Variable Parameter record. Enumeration from EBV"""
        self.detachedIndicator = 0
        """ 0 = attached, 1 = detached. See I.2.3.1 for state transition diagram"""
        self.partAttachedTo = 0
        """ the identification of the articulated part to which this articulation parameter is attached. This field shall be specified by a 16-bit unsigned integer. This field shall contain the value zero if the articulated part is attached directly to the entity."""
        self.parameterType = 0
        """ The location or station to which the part is attached"""
        self.parameterValue = 0
        """ The definition of the 64 bits shall be determined based on the type of parameter specified in the Parameter Type field """

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.recordType)
        output_stream.write_unsigned_byte(self.detachedIndicator)
        output_stream.write_unsigned_short(self.partAttachedTo)
        output_stream.write_unsigned_int(self.parameterType)
        output_stream.write_long(self.parameterValue)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_byte()
        self.detachedIndicator = input_stream.read_unsigned_byte()
        self.partAttachedTo = input_stream.read_unsigned_short()
        self.parameterType = input_stream.read_unsigned_int()
        self.parameterValue = input_stream.read_long()


class VariableTransmitterParameters(object):
    """Relates to radios. NOT COMPLETE. Section 6.2.94"""

    def __init__(self):
        """ Initializer for VariableTransmitterParameters"""
        self.recordType = 0
        """ Type of VTP. Enumeration from EBV"""
        self.recordLength = 4
        """ Length, in bytes"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_int(self.recordLength)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_int()


class Attribute(object):
    """Used to convey information for one or more attributes. Attributes conform to the standard variable record format of 6.2.82. Section 6.2.10. NOT COMPLETE"""

    def __init__(self):
        """ Initializer for Attribute"""
        self.recordType = 0
        self.recordLength = 0
        self.recordSpecificFields = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_long(self.recordSpecificFields)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.recordSpecificFields = input_stream.read_long()


class RecordQuerySpecification(object):
    """The identification of the records being queried 6.2.72"""

    def __init__(self):
        """ Initializer for RecordQuerySpecification"""
        self.numberOfRecords = 0
        self.records = []
        """ variable length list of 32 bit records"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(len(self.records))
        for anObj in self.records:
            output_stream.write_unsigned_int(anObj)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.numberOfRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfRecords):
            val = input_stream.read_unsigned_int()
            self.records.append(val)


class ArticulatedParts(object):
    """ articulated parts for movable parts and a combination of moveable/attached parts of an entity. Section 6.2.94.2"""

    def __init__(self):
        """ Initializer for ArticulatedParts"""
        self.recordType = 0
        """ the identification of the Variable Parameter record. Enumeration from EBV"""
        self.changeIndicator = 0
        """ indicate the change of any parameter for any articulated part. Starts at zero, incremented for each change """
        self.partAttachedTo = 0
        """ the identification of the articulated part to which this articulation parameter is attached. This field shall be specified by a 16-bit unsigned integer. This field shall contain the value zero if the articulated part is attached directly to the entity."""
        self.parameterType = 0
        """ the type of parameter represented, 32 bit enumeration"""
        self.parameterValue = 0
        """ The definition of the 64 bits shall be determined based on the type of parameter specified in the Parameter Type field """

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.recordType)
        output_stream.write_unsigned_byte(self.changeIndicator)
        output_stream.write_unsigned_short(self.partAttachedTo)
        output_stream.write_unsigned_int(self.parameterType)
        output_stream.write_long(self.parameterValue)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_byte()
        self.changeIndicator = input_stream.read_unsigned_byte()
        self.partAttachedTo = input_stream.read_unsigned_short()
        self.parameterType = input_stream.read_unsigned_int()
        self.parameterValue = input_stream.read_long()


class ObjectType(object):
    """The unique designation of an environmental object. Section 6.2.64"""

    def __init__(self):
        """ Initializer for ObjectType"""
        self.domain = 0
        """ Domain of entity (air, surface, subsurface, space, etc)"""
        self.objectKind = 0
        """ country to which the design of the entity is attributed"""
        self.category = 0
        """ category of entity"""
        self.subcategory = 0
        """ subcategory of entity"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.domain)
        output_stream.write_unsigned_byte(self.objectKind)
        output_stream.write_unsigned_byte(self.category)
        output_stream.write_unsigned_byte(self.subcategory)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.domain = input_stream.read_unsigned_byte()
        self.objectKind = input_stream.read_unsigned_byte()
        self.category = input_stream.read_unsigned_byte()
        self.subcategory = input_stream.read_unsigned_byte()


class Association(object):
    """An entity's associations with other entities and/or locations. For each association, this record shall specify the type of the association, the associated entity's EntityID and/or the associated location's world coordinates. This record may be used (optionally) in a transfer transaction to send internal state data from the divesting simulation to the acquiring simulation (see 5.9.4). This record may also be used for other purposes. Section 6.2.9"""

    def __init__(self):
        """ Initializer for Association"""
        self.associationType = 0
        self.padding4 = 0
        self.associatedEntityID = EntityID()
        """ identity of associated entity. If none, NO_SPECIFIC_ENTITY"""
        self.associatedLocation = Vector3Double()
        """ location, in world coordinates"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.associationType)
        output_stream.write_unsigned_byte(self.padding4)
        self.associatedEntityID.serialize(output_stream)
        self.associatedLocation.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.associationType = input_stream.read_unsigned_byte()
        self.padding4 = input_stream.read_unsigned_byte()
        self.associatedEntityID.parse(input_stream)
        self.associatedLocation.parse(input_stream)


class RecordSpecificationElement(object):
    """Synthetic record, made up from section 6.2.72. This is used to acheive a repeating variable list element."""

    def __init__(self):
        """ Initializer for RecordSpecificationElement"""
        self.recordID = 0
        """ the data structure used to convey the parameter values of the record for each record. 32 bit enumeration."""
        self.recordSetSerialNumber = 0
        """ the serial number of the first record in the block of records"""
        self.recordLength = 0
        """  the length, in bits, of the record. Note, bits, not bytes."""
        self.recordCount = 0
        """  the number of records included in the record set """
        self.recordValues = 0
        """ the concatenated records of the format specified by the Record ID field. The length of this field is the Record Length multiplied by the Record Count, in units of bits. ^^^This is wrong--variable sized data records, bit values. THis MUST be patched after generation."""
        self.pad4 = 0
        """ Padding of 0 to 31 unused bits as required for 32-bit alignment of the Record Set field. ^^^This is wrong--variable sized padding. MUST be patched post-code generation"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordID)
        output_stream.write_unsigned_int(self.recordSetSerialNumber)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_short(self.recordCount)
        output_stream.write_unsigned_short(self.recordValues)
        output_stream.write_unsigned_byte(self.pad4)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordID = input_stream.read_unsigned_int()
        self.recordSetSerialNumber = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.recordCount = input_stream.read_unsigned_short()
        self.recordValues = input_stream.read_unsigned_short()
        self.pad4 = input_stream.read_unsigned_byte()


class EightByteChunk(object):
    """64 bit piece of data"""

    def __init__(self):
        """ Initializer for EightByteChunk"""
        self.otherParameters = [0, 0, 0, 0, 0, 0, 0, 0]
        """ Eight bytes of arbitrary data"""

    def serialize(self, output_stream):
        """serialize the class """
        for idx in range(0, 8):
            output_stream.write_byte(self.otherParameters[idx])

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.otherParameters = [0] * 8
        for idx in range(0, 8):
            val = input_stream.read_byte()

            self.otherParameters[idx] = val


class AntennaLocation(object):
    """Location of the radiating portion of the antenna, specified in world coordinates and entity coordinates. Section 6.2.8"""

    def __init__(self):
        """ Initializer for AntennaLocation"""
        self.antennaLocation = Vector3Double()
        """ Location of the radiating portion of the antenna in world    coordinates"""
        self.relativeAntennaLocation = Vector3Float()
        """ Location of the radiating portion of the antenna     in entity coordinates"""

    def serialize(self, output_stream):
        """serialize the class """
        self.antennaLocation.serialize(output_stream)
        self.relativeAntennaLocation.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.antennaLocation.parse(input_stream)
        self.relativeAntennaLocation.parse(input_stream)


class ObjectIdentifier(object):
    """The unique designation of an environmental object. Section 6.2.63"""

    def __init__(self):
        """ Initializer for ObjectIdentifier"""
        self.simulationAddress = SimulationAddress()
        """  Simulation Address"""
        self.objectNumber = 0
        """ object number"""

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.objectNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.objectNumber = input_stream.read_unsigned_short()


class AggregateIdentifier(object):
    """The unique designation of each aggrgate in an exercise is specified by an aggregate identifier record. The aggregate ID is not an entity and shall not be treated as such. Section 6.2.3."""

    def __init__(self):
        """ Initializer for AggregateIdentifier"""
        self.simulationAddress = SimulationAddress()
        """ Simulation address, ie site and application, the first two fields of the entity ID"""
        self.aggregateID = 0
        """ the aggregate ID"""

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.aggregateID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.aggregateID = input_stream.read_unsigned_short()


class FixedDatum(object):
    """Fixed Datum Record. Section 6.2.38"""

    def __init__(self):
        """ Initializer for FixedDatum"""
        self.fixedDatumID = 0
        """ ID of the fixed datum, an enumeration"""
        self.fixedDatumValue = 0
        """ Value for the fixed datum"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.fixedDatumID)
        output_stream.write_unsigned_int(self.fixedDatumValue)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.fixedDatumID = input_stream.read_unsigned_int()
        self.fixedDatumValue = input_stream.read_unsigned_int()


class VariableParameter(object):
    """specification of additional information associated with an entity or detonation, not otherwise accounted for in a PDU 6.2.94.1"""

    def __init__(self):
        """ Initializer for VariableParameter"""
        self.recordType = 0
        """ the identification of the Variable Parameter record. Enumeration from EBV"""
        self.variableParameterFields1 = 0
        """ Variable parameter data fields. Two doubles minus one byte"""
        self.variableParameterFields2 = 0
        """ Variable parameter data fields. """
        self.variableParameterFields3 = 0
        """ Variable parameter data fields. """
        self.variableParameterFields4 = 0
        """ Variable parameter data fields. """

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.recordType)
        output_stream.write_double(self.variableParameterFields1)
        output_stream.write_unsigned_int(self.variableParameterFields2)
        output_stream.write_unsigned_short(self.variableParameterFields3)
        output_stream.write_unsigned_byte(self.variableParameterFields4)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_byte()
        self.variableParameterFields1 = input_stream.read_double()
        self.variableParameterFields2 = input_stream.read_unsigned_int()
        self.variableParameterFields3 = input_stream.read_unsigned_short()
        self.variableParameterFields4 = input_stream.read_unsigned_byte()


class ChangeOptions(object):
    """This is wrong and breaks serialization. See section 6.2.13 aka B.2.41"""

    def __init__(self):
        """ Initializer for ChangeOptions"""

    def serialize(self, output_stream):
        """serialize the class """

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""


class LiveSimulationAddress(object):
    """A simulation's designation associated with all Live Entity IDs contained in Live Entity PDUs. Section 6.2.55 """

    def __init__(self):
        """ Initializer for LiveSimulationAddress"""
        self.liveSiteNumber = 0
        """ facility, installation, organizational unit or geographic location may have multiple sites associated with it. The Site Number is the first component of the Live Simulation Address, which defines a live simulation."""
        self.liveApplicationNumber = 0
        """ An application associated with a live site is termed a live application. Each live application participating in an event """

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.liveSiteNumber)
        output_stream.write_unsigned_byte(self.liveApplicationNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.liveSiteNumber = input_stream.read_unsigned_byte()
        self.liveApplicationNumber = input_stream.read_unsigned_byte()


class EntityMarking(object):
    """Specifies the character set used inthe first byte, followed by 11 characters of text data. Section 6.29"""

    def __init__(self):
        """ Initializer for EntityMarking"""
        self.characterSet = 0
        """ The character set"""
        self.characters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        """ The characters"""

    def setString(self, new_str):
        for idx in range(0, 11):
            if idx < len(new_str):
                self.characters[idx] = ord(new_str[idx])
            else:
                self.characters[idx] = 0

    # convenience method to return the marking as a string, truncated of padding.
    def charactersString(self):
        return bytes(filter(None, self.characters)).decode("utf-8")

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.characterSet)
        for idx in range(0, 11):
            output_stream.write_byte(self.characters[idx])

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.characterSet = input_stream.read_unsigned_byte()
        self.characters = [0] * 11
        for idx in range(0, 11):
            val = input_stream.read_byte()

            self.characters[idx] = val


class UAFundamentalParameter(object):
    """Regeneration parameters for active emission systems that are variable throughout a scenario. Section 6.2.91"""

    def __init__(self):
        """ Initializer for UAFundamentalParameter"""
        self.activeEmissionParameterIndex = 0
        """ Which database record shall be used. An enumeration from EBV document"""
        self.scanPattern = 0
        """ The type of scan pattern, If not used, zero. An enumeration from EBV document"""
        self.beamCenterAzimuthHorizontal = 0
        """ center azimuth bearing of th emain beam. In radians."""
        self.azimuthalBeamwidthHorizontal = 0
        """ Horizontal beamwidth of th emain beam Meastued at the 3dB down point of peak radiated power. In radians."""
        self.beamCenterDepressionElevation = 0
        """ center of the d/e angle of th emain beam relative to the stablised de angle of the target. In radians."""
        self.beamwidthDownElevation = 0
        """ vertical beamwidth of the main beam. Meastured at the 3dB down point of peak radiated power. In radians."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.activeEmissionParameterIndex)
        output_stream.write_unsigned_short(self.scanPattern)
        output_stream.write_float(self.beamCenterAzimuthHorizontal)
        output_stream.write_float(self.azimuthalBeamwidthHorizontal)
        output_stream.write_float(self.beamCenterDepressionElevation)
        output_stream.write_float(self.beamwidthDownElevation)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.activeEmissionParameterIndex = input_stream.read_unsigned_short()
        self.scanPattern = input_stream.read_unsigned_short()
        self.beamCenterAzimuthHorizontal = input_stream.read_float()
        self.azimuthalBeamwidthHorizontal = input_stream.read_float()
        self.beamCenterDepressionElevation = input_stream.read_float()
        self.beamwidthDownElevation = input_stream.read_float()


class TwoByteChunk(object):
    """16 bit piece of data"""

    def __init__(self):
        """ Initializer for TwoByteChunk"""
        self.otherParameters = [0, 0]
        """ two bytes of arbitrary data"""

    def serialize(self, output_stream):
        """serialize the class """
        for idx in range(0, 2):
            output_stream.write_byte(self.otherParameters[idx])

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.otherParameters = [0] * 2
        for idx in range(0, 2):
            val = input_stream.read_byte()

            self.otherParameters[idx] = val


class DirectedEnergyDamage(object):
    """Damage sustained by an entity due to directed energy. Location of the damage based on a relative x,y,z location from the center of the entity. Section 6.2.15.2"""

    def __init__(self):
        """ Initializer for DirectedEnergyDamage"""
        self.recordType = 4500
        """ DE Record Type."""
        self.recordLength = 40
        """ DE Record Length (bytes)."""
        self.padding = 0
        """ padding."""
        self.damageLocation = Vector3Float()
        """ location of damage, relative to center of entity"""
        self.damageDiameter = 0
        """ Size of damaged area, in meters."""
        self.temperature = -273.15
        """ average temp of the damaged area, in degrees celsius. If firing entitty does not model this, use a value of -273.15"""
        self.componentIdentification = 0
        """ enumeration"""
        self.componentDamageStatus = 0
        """ enumeration"""
        self.componentVisualDamageStatus = 0
        """ enumeration"""
        self.componentVisualSmokeColor = 0
        """ enumeration"""
        self.fireEventID = EventIdentifier()
        """ For any component damage resulting this field shall be set to the fire event ID from that PDU."""
        self.padding2 = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_short(self.padding)
        self.damageLocation.serialize(output_stream)
        output_stream.write_float(self.damageDiameter)
        output_stream.write_float(self.temperature)
        output_stream.write_unsigned_byte(self.componentIdentification)
        output_stream.write_unsigned_byte(self.componentDamageStatus)
        output_stream.write_unsigned_byte(self.componentVisualDamageStatus)
        output_stream.write_unsigned_byte(self.componentVisualSmokeColor)
        self.fireEventID.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding2)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()
        self.damageLocation.parse(input_stream)
        self.damageDiameter = input_stream.read_float()
        self.temperature = input_stream.read_float()
        self.componentIdentification = input_stream.read_unsigned_byte()
        self.componentDamageStatus = input_stream.read_unsigned_byte()
        self.componentVisualDamageStatus = input_stream.read_unsigned_byte()
        self.componentVisualSmokeColor = input_stream.read_unsigned_byte()
        self.fireEventID.parse(input_stream)
        self.padding2 = input_stream.read_unsigned_short()


class ExplosionDescriptor(object):
    """Explosion of a non-munition. Section 6.2.19.3"""

    def __init__(self):
        """ Initializer for ExplosionDescriptor"""
        self.explodingObject = EntityType()
        """ Type of the object that exploded. See 6.2.30"""
        self.explosiveMaterial = 0
        """ Material that exploded. Can be grain dust, tnt, gasoline, etc. Enumeration"""
        self.padding = 0
        """ padding"""
        self.explosiveForce = 0
        """ Force of explosion, in equivalent KG of TNT"""

    def serialize(self, output_stream):
        """serialize the class """
        self.explodingObject.serialize(output_stream)
        output_stream.write_unsigned_short(self.explosiveMaterial)
        output_stream.write_unsigned_short(self.padding)
        output_stream.write_float(self.explosiveForce)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.explodingObject.parse(input_stream)
        self.explosiveMaterial = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()
        self.explosiveForce = input_stream.read_float()


class ClockTime(object):
    """Time measurements that exceed one hour are represented by this record. The first field is the hours since the unix epoch (Jan 1 1970, used by most Unix systems and java) and the second field the timestamp units since the top of the hour. Section 6.2.14"""

    def __init__(self):
        """ Initializer for ClockTime"""
        self.hour = 0
        """ Hours in UTC"""
        self.timePastHour = 0
        """ Time past the hour"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.hour)
        output_stream.write_unsigned_int(self.timePastHour)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.hour = input_stream.read_unsigned_int()
        self.timePastHour = input_stream.read_unsigned_int()


class SecondaryOperationalData(object):
    """Additional operational data for an IFF emitting system and the number of IFF Fundamental Parameter Data records Section 6.2.76."""

    def __init__(self):
        """ Initializer for SecondaryOperationalData"""
        self.operationalData1 = 0
        """ additional operational characteristics of the IFF emitting system. Each 8-bit field will vary depending on the system type."""
        self.operationalData2 = 0
        """ additional operational characteristics of the IFF emitting system. Each 8-bit field will vary depending on the system type."""
        self.numberOfIFFFundamentalParameterRecords = 0
        """ the number of IFF Fundamental Parameter Data records that follow"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.operationalData1)
        output_stream.write_unsigned_byte(self.operationalData2)
        output_stream.write_unsigned_short(self.numberOfIFFFundamentalParameterRecords)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.operationalData1 = input_stream.read_unsigned_byte()
        self.operationalData2 = input_stream.read_unsigned_byte()
        self.numberOfIFFFundamentalParameterRecords = input_stream.read_unsigned_short()


class EnvironmentType(object):
    """Description of environmental data in environmental process and gridded data PDUs. Section 6.2.32"""

    def __init__(self):
        """ Initializer for EnvironmentType"""
        self.entityKind = 0
        """ Kind of entity"""
        self.domain = 0
        """ Domain of entity (air, surface, subsurface, space, etc)"""
        self.entityClass = 0
        """ class of environmental entity"""
        self.category = 0
        """ category of entity"""
        self.subcategory = 0
        """ subcategory of entity"""
        self.specific = 0
        """ specific info based on subcategory field"""
        self.extra = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.entityKind)
        output_stream.write_unsigned_byte(self.domain)
        output_stream.write_unsigned_short(self.entityClass)
        output_stream.write_unsigned_byte(self.category)
        output_stream.write_unsigned_byte(self.subcategory)
        output_stream.write_unsigned_byte(self.specific)
        output_stream.write_unsigned_byte(self.extra)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.entityKind = input_stream.read_unsigned_byte()
        self.domain = input_stream.read_unsigned_byte()
        self.entityClass = input_stream.read_unsigned_short()
        self.category = input_stream.read_unsigned_byte()
        self.subcategory = input_stream.read_unsigned_byte()
        self.specific = input_stream.read_unsigned_byte()
        self.extra = input_stream.read_unsigned_byte()


class TotalRecordSets(object):
    """Total number of record sets contained in a logical set of one or more PDUs. Used to transfer ownership, etc Section 6.2.88"""

    def __init__(self):
        """ Initializer for TotalRecordSets"""
        self.totalRecordSets = 0
        """ Total number of record sets"""
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.totalRecordSets)
        output_stream.write_unsigned_short(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.totalRecordSets = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()


class MineEntityIdentifier(object):
    """The unique designation of a mine contained in the Minefield Data PDU. No espdus are issued for mine entities.  Section 6.2.55 """

    def __init__(self):
        """ Initializer for MineEntityIdentifier"""
        self.simulationAddress = SimulationAddress()
        """ """
        self.mineEntityNumber = 0
        """ """

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.mineEntityNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.mineEntityNumber = input_stream.read_unsigned_short()


class Relationship(object):
    """The relationship of the part entity to its host entity. Section 6.2.74."""

    def __init__(self):
        """ Initializer for Relationship"""
        self.nature = 0
        """ the nature or purpose for joining of the part entity to the host entity and shall be represented by a 16-bit enumeration"""
        self.position = 0
        """ the position of the part entity with respect to the host entity and shall be represented by a 16-bit enumeration"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.nature)
        output_stream.write_unsigned_short(self.position)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.nature = input_stream.read_unsigned_short()
        self.position = input_stream.read_unsigned_short()


class EEFundamentalParameterData(object):
    """Contains electromagnetic emmission regeneration parameters that are variable throught a scenario. Section 6.2.22."""

    def __init__(self):
        """ Initializer for EEFundamentalParameterData"""
        self.frequency = 0
        """ center frequency of the emission in hertz."""
        self.frequencyRange = 0
        """ Bandwidth of the frequencies corresponding to the fequency field."""
        self.effectiveRadiatedPower = 0
        """ Effective radiated power for the emission in DdBm. For a radar noise jammer, indicates the peak of the transmitted power."""
        self.pulseRepetitionFrequency = 0
        """ Average repetition frequency of the emission in hertz."""
        self.pulseWidth = 0
        """ Average pulse width  of the emission in microseconds."""
        self.beamAzimuthCenter = 0
        self.beamAzimuthSweep = 0
        self.beamElevationCenter = 0
        self.beamElevationSweep = 0
        self.beamSweepSync = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.frequency)
        output_stream.write_float(self.frequencyRange)
        output_stream.write_float(self.effectiveRadiatedPower)
        output_stream.write_float(self.pulseRepetitionFrequency)
        output_stream.write_float(self.pulseWidth)
        output_stream.write_float(self.beamAzimuthCenter)
        output_stream.write_float(self.beamAzimuthSweep)
        output_stream.write_float(self.beamElevationCenter)
        output_stream.write_float(self.beamElevationSweep)
        output_stream.write_float(self.beamSweepSync)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.frequency = input_stream.read_float()
        self.frequencyRange = input_stream.read_float()
        self.effectiveRadiatedPower = input_stream.read_float()
        self.pulseRepetitionFrequency = input_stream.read_float()
        self.pulseWidth = input_stream.read_float()
        self.beamAzimuthCenter = input_stream.read_float()
        self.beamAzimuthSweep = input_stream.read_float()
        self.beamElevationCenter = input_stream.read_float()
        self.beamElevationSweep = input_stream.read_float()
        self.beamSweepSync = input_stream.read_float()


class JammingTechnique(object):
    """Jamming technique. Section 6.2.49"""

    def __init__(self):
        """ Initializer for JammingTechnique"""
        self.kind = 0
        self.category = 0
        self.subcategory = 0
        self.specific = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.kind)
        output_stream.write_unsigned_byte(self.category)
        output_stream.write_unsigned_byte(self.subcategory)
        output_stream.write_unsigned_byte(self.specific)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.kind = input_stream.read_unsigned_byte()
        self.category = input_stream.read_unsigned_byte()
        self.subcategory = input_stream.read_unsigned_byte()
        self.specific = input_stream.read_unsigned_byte()


class DatumSpecification(object):
    """List of fixed and variable datum records. Section 6.2.18 """

    def __init__(self):
        """ Initializer for DatumSpecification"""
        self.numberOfFixedDatums = 0
        """ Number of fixed datums"""
        self.numberOfVariableDatums = 0
        """ Number of variable datums"""
        self.fixedDatumIDList = []
        """ variable length list fixed datums"""
        self.variableDatumIDList = []
        """ variable length list variable datums"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(len(self.fixedDatumIDList))
        output_stream.write_unsigned_int(len(self.variableDatumIDList))
        for anObj in self.fixedDatumIDList:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumIDList:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.numberOfFixedDatums = input_stream.read_unsigned_int()
        self.numberOfVariableDatums = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatums):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumIDList.append(element)

        for idx in range(0, self.numberOfVariableDatums):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumIDList.append(element)


class DirectedEnergyAreaAimpoint(object):
    """DE Precision Aimpoint Record. NOT COMPLETE. Section 6.2.20.2"""

    def __init__(self):
        """ Initializer for DirectedEnergyAreaAimpoint"""
        self.recordType = 4001
        """ Type of Record enumeration"""
        self.recordLength = 0
        """ Length of Record"""
        self.padding = 0
        """ Padding"""
        self.beamAntennaPatternRecordCount = 0
        """ Number of beam antenna pattern records"""
        self.directedEnergyTargetEnergyDepositionRecordCount = 0
        """ Number of DE target energy depositon records"""
        self.beamAntennaParameterList = []
        """ list of beam antenna records. See 6.2.9.2"""
        self.directedEnergyTargetEnergyDepositionRecordList = []
        """ list of DE target deposition records. See 6.2.21.4"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_short(self.padding)
        output_stream.write_unsigned_short(len(self.beamAntennaParameterList))
        output_stream.write_unsigned_short(len(self.directedEnergyTargetEnergyDepositionRecordList))
        for anObj in self.beamAntennaParameterList:
            anObj.serialize(output_stream)

        for anObj in self.directedEnergyTargetEnergyDepositionRecordList:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()
        self.beamAntennaPatternRecordCount = input_stream.read_unsigned_short()
        self.directedEnergyTargetEnergyDepositionRecordCount = input_stream.read_unsigned_short()
        for idx in range(0, self.beamAntennaPatternRecordCount):
            element = null()
            element.parse(input_stream)
            self.beamAntennaParameterList.append(element)

        for idx in range(0, self.directedEnergyTargetEnergyDepositionRecordCount):
            element = null()
            element.parse(input_stream)
            self.directedEnergyTargetEnergyDepositionRecordList.append(element)


class Vector3Float(object):
    """Three floating point values, x, y, and z. Section 6.2.95"""

    def __init__(self):
        """ Initializer for Vector3Float"""
        self.x = 0
        """ X value"""
        self.y = 0
        """ y Value"""
        self.z = 0
        """ Z value"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.x)
        output_stream.write_float(self.y)
        output_stream.write_float(self.z)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.x = input_stream.read_float()
        self.y = input_stream.read_float()
        self.z = input_stream.read_float()


class Expendable(object):
    """An entity's expendable (chaff, flares, etc) information. Section 6.2.36"""

    def __init__(self):
        """ Initializer for Expendable"""
        self.expendable = EntityType()
        """ Type of expendable"""
        self.station = 0
        self.quantity = 0
        self.expendableStatus = 0
        self.padding = 0

    def serialize(self, output_stream):
        """serialize the class """
        self.expendable.serialize(output_stream)
        output_stream.write_unsigned_int(self.station)
        output_stream.write_unsigned_short(self.quantity)
        output_stream.write_unsigned_byte(self.expendableStatus)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.expendable.parse(input_stream)
        self.station = input_stream.read_unsigned_int()
        self.quantity = input_stream.read_unsigned_short()
        self.expendableStatus = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class IOCommunicationsNode(object):
    """A communications node that is part of a simulted communcations network. Section 6.2.49.2"""

    def __init__(self):
        """ Initializer for IOCommunicationsNode"""
        self.recordType = 5501
        self.recordLength = 16
        self.communcationsNodeType = 0
        self.padding = 0
        self.communicationsNodeID = CommunicationsNodeID()

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_byte(self.communcationsNodeType)
        output_stream.write_unsigned_byte(self.padding)
        self.communicationsNodeID.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.communcationsNodeType = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()
        self.communicationsNodeID.parse(input_stream)


class ModulationType(object):
    """Information about the type of modulation used for radio transmission. 6.2.59 """

    def __init__(self):
        """ Initializer for ModulationType"""
        self.spreadSpectrum = 0
        """ This field shall indicate the spread spectrum technique or combination of spread spectrum techniques in use. Bit field. 0=freq hopping, 1=psuedo noise, time hopping=2, reamining bits unused"""
        self.majorModulation = 0
        """ the major classification of the modulation type. """
        self.detail = 0
        """ provide certain detailed information depending upon the major modulation type"""
        self.radioSystem = 0
        """ the radio system associated with this Transmitter PDU and shall be used as the basis to interpret other fields whose values depend on a specific radio system."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.spreadSpectrum)
        output_stream.write_unsigned_short(self.majorModulation)
        output_stream.write_unsigned_short(self.detail)
        output_stream.write_unsigned_short(self.radioSystem)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.spreadSpectrum = input_stream.read_unsigned_short()
        self.majorModulation = input_stream.read_unsigned_short()
        self.detail = input_stream.read_unsigned_short()
        self.radioSystem = input_stream.read_unsigned_short()


class LinearSegmentParameter(object):
    """The specification of an individual segment of a linear segment synthetic environment object in a Linear Object State PDU Section 6.2.52"""

    def __init__(self):
        """ Initializer for LinearSegmentParameter"""
        self.segmentNumber = 0
        """ the individual segment of the linear segment """
        self.segmentModification = 0
        """  whether a modification has been made to the point objects location or orientation"""
        self.generalSegmentAppearance = 0
        """ general dynamic appearance attributes of the segment. This record shall be defined as a 16-bit record of enumerations. The values defined for this record are included in Section 12 of SISO-REF-010."""
        self.specificSegmentAppearance = 0
        """ This field shall specify specific dynamic appearance attributes of the segment. This record shall be defined as a 32-bit record of enumerations."""
        self.segmentLocation = Vector3Double()
        """ This field shall specify the location of the linear segment in the simulated world and shall be represented by a World Coordinates record """
        self.segmentOrientation = EulerAngles()
        """ orientation of the linear segment about the segment location and shall be represented by a Euler Angles record """
        self.segmentLength = 0
        """ length of the linear segment, in meters, extending in the positive X direction"""
        self.segmentWidth = 0
        """ The total width of the linear segment, in meters, shall be specified by a 16-bit unsigned integer. One-half of the width shall extend in the positive Y direction, and one-half of the width shall extend in the negative Y direction."""
        self.segmentHeight = 0
        """ The height of the linear segment, in meters, above ground shall be specified by a 16-bit unsigned integer."""
        self.segmentDepth = 0
        """ The depth of the linear segment, in meters, below ground level """
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.segmentNumber)
        output_stream.write_unsigned_byte(self.segmentModification)
        output_stream.write_unsigned_short(self.generalSegmentAppearance)
        output_stream.write_unsigned_int(self.specificSegmentAppearance)
        self.segmentLocation.serialize(output_stream)
        self.segmentOrientation.serialize(output_stream)
        output_stream.write_float(self.segmentLength)
        output_stream.write_float(self.segmentWidth)
        output_stream.write_float(self.segmentHeight)
        output_stream.write_float(self.segmentDepth)
        output_stream.write_unsigned_int(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.segmentNumber = input_stream.read_unsigned_byte()
        self.segmentModification = input_stream.read_unsigned_byte()
        self.generalSegmentAppearance = input_stream.read_unsigned_short()
        self.specificSegmentAppearance = input_stream.read_unsigned_int()
        self.segmentLocation.parse(input_stream)
        self.segmentOrientation.parse(input_stream)
        self.segmentLength = input_stream.read_float()
        self.segmentWidth = input_stream.read_float()
        self.segmentHeight = input_stream.read_float()
        self.segmentDepth = input_stream.read_float()
        self.padding = input_stream.read_unsigned_int()


class SimulationAddress(object):
    """A Simulation Address record shall consist of the Site Identification number and the Application Identification number. Section 6.2.79 """

    def __init__(self):
        """ Initializer for SimulationAddress"""
        self.site = 0
        """ A site is defined as a facility, installation, organizational unit or a geographic location that has one or more simulation applications capable of participating in a distributed event. """
        self.application = 0
        """ An application is defined as a software program that is used to generate and process distributed simulation data including live, virtual and constructive data."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.site)
        output_stream.write_unsigned_short(self.application)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.site = input_stream.read_unsigned_short()
        self.application = input_stream.read_unsigned_short()


class SystemIdentifier(object):
    """The ID of the IFF emitting system. NOT COMPLETE. Section 6.2.87"""

    def __init__(self):
        """ Initializer for SystemIdentifier"""
        self.systemType = 0
        """ general type of emitting system, an enumeration"""
        self.systemName = 0
        """ named type of system, an enumeration"""
        self.systemMode = 0
        """ mode of operation for the system, an enumeration"""
        self.changeOptions = ChangeOptions()
        """ status of this PDU, see section 6.2.15"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.systemType)
        output_stream.write_unsigned_short(self.systemName)
        output_stream.write_unsigned_short(self.systemMode)
        self.changeOptions.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.systemType = input_stream.read_unsigned_short()
        self.systemName = input_stream.read_unsigned_short()
        self.systemMode = input_stream.read_unsigned_short()
        self.changeOptions.parse(input_stream)


class TrackJamData(object):
    """ Track-Jam data Section 6.2.89"""

    def __init__(self):
        """ Initializer for TrackJamData"""
        self.entityID = EntityID()
        """ the entity tracked or illumated, or an emitter beam targeted with jamming"""
        self.emitterNumber = 0
        """ Emitter system associated with the entity"""
        self.beamNumber = 0
        """ Beam associated with the entity"""

    def serialize(self, output_stream):
        """serialize the class """
        self.entityID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.emitterNumber)
        output_stream.write_unsigned_byte(self.beamNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.entityID.parse(input_stream)
        self.emitterNumber = input_stream.read_unsigned_byte()
        self.beamNumber = input_stream.read_unsigned_byte()


class AggregateType(object):
    """Identifies the type and organization of an aggregate. Section 6.2.5"""

    def __init__(self):
        """ Initializer for AggregateType"""
        self.aggregateKind = 0
        """ Grouping criterion used to group the aggregate. Enumeration from EBV document"""
        self.domain = 0
        """ Domain of entity (air, surface, subsurface, space, etc) Zero means domain does not apply."""
        self.country = 0
        """ country to which the design of the entity is attributed"""
        self.category = 0
        """ category of entity"""
        self.subcategory = 0
        """ subcategory of entity"""
        self.specificInfo = 0
        """ specific info based on subcategory field. specific is a reserved word in sql."""
        self.extra = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.aggregateKind)
        output_stream.write_unsigned_byte(self.domain)
        output_stream.write_unsigned_short(self.country)
        output_stream.write_unsigned_byte(self.category)
        output_stream.write_unsigned_byte(self.subcategory)
        output_stream.write_unsigned_byte(self.specificInfo)
        output_stream.write_unsigned_byte(self.extra)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.aggregateKind = input_stream.read_unsigned_byte()
        self.domain = input_stream.read_unsigned_byte()
        self.country = input_stream.read_unsigned_short()
        self.category = input_stream.read_unsigned_byte()
        self.subcategory = input_stream.read_unsigned_byte()
        self.specificInfo = input_stream.read_unsigned_byte()
        self.extra = input_stream.read_unsigned_byte()


class SimulationManagementPduHeader(object):
    """First part of a simulation management (SIMAN) PDU and SIMAN-Reliability (SIMAN-R) PDU. Sectionn 6.2.81"""

    def __init__(self):
        """ Initializer for SimulationManagementPduHeader"""
        self.pduHeader = PduHeader()
        """ Conventional PDU header"""
        self.originatingID = SimulationIdentifier()
        """ IDs the simulation or entity, etiehr a simulation or an entity. Either 6.2.80 or 6.2.28"""
        self.receivingID = SimulationIdentifier()
        """ simulation, all simulations, a special ID, or an entity. See 5.6.5 and 5.12.4"""

    def serialize(self, output_stream):
        """serialize the class """
        self.pduHeader.serialize(output_stream)
        self.originatingID.serialize(output_stream)
        self.receivingID.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.pduHeader.parse(input_stream)
        self.originatingID.parse(input_stream)
        self.receivingID.parse(input_stream)


class BeamData(object):
    """Describes the scan volue of an emitter beam. Section 6.2.11."""

    def __init__(self):
        """ Initializer for BeamData"""
        self.beamAzimuthCenter = 0
        """ Specifies the beam azimuth an elevation centers and corresponding half-angles to describe the scan volume"""
        self.beamAzimuthSweep = 0
        """ Specifies the beam azimuth sweep to determine scan volume"""
        self.beamElevationCenter = 0
        """ Specifies the beam elevation center to determine scan volume"""
        self.beamElevationSweep = 0
        """ Specifies the beam elevation sweep to determine scan volume"""
        self.beamSweepSync = 0
        """ allows receiver to synchronize its regenerated scan pattern to that of the emmitter. Specifies the percentage of time a scan is through its pattern from its origion."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.beamAzimuthCenter)
        output_stream.write_float(self.beamAzimuthSweep)
        output_stream.write_float(self.beamElevationCenter)
        output_stream.write_float(self.beamElevationSweep)
        output_stream.write_float(self.beamSweepSync)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.beamAzimuthCenter = input_stream.read_float()
        self.beamAzimuthSweep = input_stream.read_float()
        self.beamElevationCenter = input_stream.read_float()
        self.beamElevationSweep = input_stream.read_float()
        self.beamSweepSync = input_stream.read_float()


class EngineFuel(object):
    """Information about an entity's engine fuel. Section 6.2.24."""

    def __init__(self):
        """ Initializer for EngineFuel"""
        self.fuelQuantity = 0
        """ Fuel quantity, units specified by next field"""
        self.fuelMeasurementUnits = 0
        """ Units in which the fuel is measured"""
        self.fuelType = 0
        """ Type of fuel"""
        self.fuelLocation = 0
        """ Location of fuel as related to entity. See section 14 of EBV document"""
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.fuelQuantity)
        output_stream.write_unsigned_byte(self.fuelMeasurementUnits)
        output_stream.write_unsigned_byte(self.fuelType)
        output_stream.write_unsigned_byte(self.fuelLocation)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.fuelQuantity = input_stream.read_unsigned_int()
        self.fuelMeasurementUnits = input_stream.read_unsigned_byte()
        self.fuelType = input_stream.read_unsigned_byte()
        self.fuelLocation = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class IOEffect(object):
    """Effect of IO on an entity. Section 6.2.49.3"""

    def __init__(self):
        """ Initializer for IOEffect"""
        self.recordType = 5500
        self.recordLength = 16
        self.ioStatus = 0
        self.ioLinkType = 0
        self.ioEffect = EntityID()
        self.ioEffectDutyCycle = 0
        self.ioEffectDuration = 0
        self.ioProcess = 0
        self.padding = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_byte(self.ioStatus)
        output_stream.write_unsigned_byte(self.ioLinkType)
        self.ioEffect.serialize(output_stream)
        output_stream.write_unsigned_byte(self.ioEffectDutyCycle)
        output_stream.write_unsigned_short(self.ioEffectDuration)
        output_stream.write_unsigned_short(self.ioProcess)
        output_stream.write_unsigned_short(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.ioStatus = input_stream.read_unsigned_byte()
        self.ioLinkType = input_stream.read_unsigned_byte()
        self.ioEffect.parse(input_stream)
        self.ioEffectDutyCycle = input_stream.read_unsigned_byte()
        self.ioEffectDuration = input_stream.read_unsigned_short()
        self.ioProcess = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()


class SimulationIdentifier(object):
    """The unique designation of a simulation when using the 48-bit identifier format shall be specified by the Sim- ulation Identifier record. The reason that the 48-bit format is required in addition to the 32-bit simulation address format that actually identifies a specific simulation is because some 48-bit identifier fields in PDUs may contain either an Object Identifier, such as an Entity ID, or a Simulation Identifier. Section 6.2.80"""

    def __init__(self):
        """ Initializer for SimulationIdentifier"""
        self.simulationAddress = SimulationAddress()
        """ Simulation address """
        self.referenceNumber = 0
        """ This field shall be set to zero as there is no reference number associated with a Simulation Identifier."""

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.referenceNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.referenceNumber = input_stream.read_unsigned_short()


class GridAxisDescriptorVariable(object):
    """Grid axis descriptor fo variable spacing axis data. NOT COMPLETE. Need padding to 64 bit boundary."""

    def __init__(self):
        """ Initializer for GridAxisDescriptorVariable"""
        self.domainInitialXi = 0
        """ coordinate of the grid origin or initial value"""
        self.domainFinalXi = 0
        """ coordinate of the endpoint or final value"""
        self.domainPointsXi = 0
        """ The number of grid points along the Xi domain axis for the enviornmental state data"""
        self.interleafFactor = 0
        """ interleaf factor along the domain axis."""
        self.axisType = 0
        """ type of grid axis"""
        self.numberOfPointsOnXiAxis = 0
        """ Number of grid locations along Xi axis"""
        self.initialIndex = 0
        """ initial grid point for the current pdu"""
        self.coordinateScaleXi = 0
        """ value that linearly scales the coordinates of the grid locations for the xi axis"""
        self.coordinateOffsetXi = 0.0
        """ The constant offset value that shall be applied to the grid locations for the xi axis"""
        self.xiValues = []
        """ list of coordinates"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_double(self.domainInitialXi)
        output_stream.write_double(self.domainFinalXi)
        output_stream.write_unsigned_short(self.domainPointsXi)
        output_stream.write_unsigned_byte(self.interleafFactor)
        output_stream.write_unsigned_byte(self.axisType)
        output_stream.write_unsigned_short(len(self.xiValues))
        output_stream.write_unsigned_short(self.initialIndex)
        output_stream.write_double(self.coordinateScaleXi)
        output_stream.write_double(self.coordinateOffsetXi)
        for anObj in self.xiValues:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.domainInitialXi = input_stream.read_double()
        self.domainFinalXi = input_stream.read_double()
        self.domainPointsXi = input_stream.read_unsigned_short()
        self.interleafFactor = input_stream.read_unsigned_byte()
        self.axisType = input_stream.read_unsigned_byte()
        self.numberOfPointsOnXiAxis = input_stream.read_unsigned_short()
        self.initialIndex = input_stream.read_unsigned_short()
        self.coordinateScaleXi = input_stream.read_double()
        self.coordinateOffsetXi = input_stream.read_double()
        for idx in range(0, self.numberOfPointsOnXiAxis):
            element = null()
            element.parse(input_stream)
            self.xiValues.append(element)


class SupplyQuantity(object):
    """ A supply, and the amount of that supply. Section 6.2.86"""

    def __init__(self):
        """ Initializer for SupplyQuantity"""
        self.supplyType = EntityType()
        """ Type of supply"""
        self.quantity = 0
        """ the number of units of a supply type. """

    def serialize(self, output_stream):
        """serialize the class """
        self.supplyType.serialize(output_stream)
        output_stream.write_float(self.quantity)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.supplyType.parse(input_stream)
        self.quantity = input_stream.read_float()


class SilentEntitySystem(object):
    """information abou an enitity not producing espdus. Section 6.2.79"""

    def __init__(self):
        """ Initializer for SilentEntitySystem"""
        self.numberOfEntities = 0
        """ number of the type specified by the entity type field"""
        self.numberOfAppearanceRecords = 0
        """ number of entity appearance records that follow"""
        self.entityType = EntityType()
        """ Entity type"""
        self.appearanceRecordList = []
        """ Variable length list of appearance records"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.numberOfEntities)
        output_stream.write_unsigned_short(len(self.appearanceRecordList))
        self.entityType.serialize(output_stream)
        for anObj in self.appearanceRecordList:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.numberOfEntities = input_stream.read_unsigned_short()
        self.numberOfAppearanceRecords = input_stream.read_unsigned_short()
        self.entityType.parse(input_stream)
        for idx in range(0, self.numberOfAppearanceRecords):
            element = null()
            element.parse(input_stream)
            self.appearanceRecordList.append(element)


class EventIdentifier(object):
    """Identifies an event in the world. Use this format for every PDU EXCEPT the LiveEntityPdu. Section 6.2.34."""

    def __init__(self):
        """ Initializer for EventIdentifier"""
        self.simulationAddress = SimulationAddress()
        """ Site and application IDs"""
        self.eventNumber = 0

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.eventNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.eventNumber = input_stream.read_unsigned_short()


class BlankingSector(object):
    """The Blanking Sector attribute record may be used to convey persistent areas within a scan volume where emitter power for a specific active emitter beam is reduced to an insignificant value. Section 6.2.21.2"""

    def __init__(self):
        """ Initializer for BlankingSector"""
        self.recordType = 3500
        self.recordLength = 40
        self.padding = 0
        self.emitterNumber = 0
        self.beamNumber = 0
        self.stateIndicator = 0
        self.padding2 = 0
        self.leftAzimuth = 0
        self.rightAzimuth = 0
        self.lowerElevation = 0
        self.upperElevation = 0
        self.residualPower = 0
        self.padding3 = 0
        self.padding4 = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_int(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_short(self.padding)
        output_stream.write_unsigned_byte(self.emitterNumber)
        output_stream.write_unsigned_byte(self.beamNumber)
        output_stream.write_unsigned_byte(self.stateIndicator)
        output_stream.write_unsigned_byte(self.padding2)
        output_stream.write_float(self.leftAzimuth)
        output_stream.write_float(self.rightAzimuth)
        output_stream.write_float(self.lowerElevation)
        output_stream.write_float(self.upperElevation)
        output_stream.write_float(self.residualPower)
        output_stream.write_int(self.padding3)
        output_stream.write_int(self.padding4)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_int()
        self.recordLength = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()
        self.emitterNumber = input_stream.read_unsigned_byte()
        self.beamNumber = input_stream.read_unsigned_byte()
        self.stateIndicator = input_stream.read_unsigned_byte()
        self.padding2 = input_stream.read_unsigned_byte()
        self.leftAzimuth = input_stream.read_float()
        self.rightAzimuth = input_stream.read_float()
        self.lowerElevation = input_stream.read_float()
        self.upperElevation = input_stream.read_float()
        self.residualPower = input_stream.read_float()
        self.padding3 = input_stream.read_int()
        self.padding4 = input_stream.read_int()


class LaunchedMunitionRecord(object):
    """Identity of a communications node. Section 6.2.50"""

    def __init__(self):
        """ Initializer for LaunchedMunitionRecord"""
        self.fireEventID = EventIdentifier()
        self.padding = 0
        self.firingEntityID = EventIdentifier()
        self.padding2 = 0
        self.targetEntityID = EventIdentifier()
        self.padding3 = 0
        self.targetLocation = Vector3Double()

    def serialize(self, output_stream):
        """serialize the class """
        self.fireEventID.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding)
        self.firingEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding2)
        self.targetEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding3)
        self.targetLocation.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.fireEventID.parse(input_stream)
        self.padding = input_stream.read_unsigned_short()
        self.firingEntityID.parse(input_stream)
        self.padding2 = input_stream.read_unsigned_short()
        self.targetEntityID.parse(input_stream)
        self.padding3 = input_stream.read_unsigned_short()
        self.targetLocation.parse(input_stream)


class IFFFundamentalParameterData(object):
    """Fundamental IFF atc data. Section 6.2.45"""

    def __init__(self):
        """ Initializer for IFFFundamentalParameterData"""
        self.erp = 0
        """ ERP"""
        self.frequency = 0
        """ frequency"""
        self.pgrf = 0
        """ pgrf"""
        self.pulseWidth = 0
        """ Pulse width"""
        self.burstLength = 0
        """ Burst length"""
        self.applicableModes = 0
        """ Applicable modes enumeration"""
        self.systemSpecificData = [0, 0, 0]
        """ System-specific data"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.erp)
        output_stream.write_float(self.frequency)
        output_stream.write_float(self.pgrf)
        output_stream.write_float(self.pulseWidth)
        output_stream.write_unsigned_int(self.burstLength)
        output_stream.write_unsigned_byte(self.applicableModes)
        for idx in range(0, 3):
            output_stream.write_unsigned_byte(self.systemSpecificData[idx])

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.erp = input_stream.read_float()
        self.frequency = input_stream.read_float()
        self.pgrf = input_stream.read_float()
        self.pulseWidth = input_stream.read_float()
        self.burstLength = input_stream.read_unsigned_int()
        self.applicableModes = input_stream.read_unsigned_byte()
        self.systemSpecificData = [0] * 3
        for idx in range(0, 3):
            val = input_stream.read_unsigned_byte()

            self.systemSpecificData[idx] = val


class FundamentalOperationalData(object):
    """Basic operational data for IFF. Section 6.2.40."""

    def __init__(self):
        """ Initializer for FundamentalOperationalData"""
        self.systemStatus = 0
        """ system status"""
        self.dataField1 = 0
        """ data field 1"""
        self.informationLayers = 0
        """ eight boolean fields"""
        self.dataField2 = 0
        """ enumeration"""
        self.parameter1 = 0
        """ parameter, enumeration"""
        self.parameter2 = 0
        """ parameter, enumeration"""
        self.parameter3 = 0
        """ parameter, enumeration"""
        self.parameter4 = 0
        """ parameter, enumeration"""
        self.parameter5 = 0
        """ parameter, enumeration"""
        self.parameter6 = 0
        """ parameter, enumeration"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.systemStatus)
        output_stream.write_unsigned_byte(self.dataField1)
        output_stream.write_unsigned_byte(self.informationLayers)
        output_stream.write_unsigned_byte(self.dataField2)
        output_stream.write_unsigned_short(self.parameter1)
        output_stream.write_unsigned_short(self.parameter2)
        output_stream.write_unsigned_short(self.parameter3)
        output_stream.write_unsigned_short(self.parameter4)
        output_stream.write_unsigned_short(self.parameter5)
        output_stream.write_unsigned_short(self.parameter6)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.systemStatus = input_stream.read_unsigned_byte()
        self.dataField1 = input_stream.read_unsigned_byte()
        self.informationLayers = input_stream.read_unsigned_byte()
        self.dataField2 = input_stream.read_unsigned_byte()
        self.parameter1 = input_stream.read_unsigned_short()
        self.parameter2 = input_stream.read_unsigned_short()
        self.parameter3 = input_stream.read_unsigned_short()
        self.parameter4 = input_stream.read_unsigned_short()
        self.parameter5 = input_stream.read_unsigned_short()
        self.parameter6 = input_stream.read_unsigned_short()


class IntercomCommunicationsParameters(object):
    """Intercom communcations parameters. Section 6.2.47.  This requires hand coding"""

    def __init__(self):
        """ Initializer for IntercomCommunicationsParameters"""
        self.recordType = 0
        """ Type of intercom parameters record"""
        self.recordLength = 0
        """ length of record"""
        self.recordSpecificField = 0
        """ This is a placeholder."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.recordType)
        output_stream.write_unsigned_short(self.recordLength)
        output_stream.write_unsigned_int(self.recordSpecificField)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_short()
        self.recordLength = input_stream.read_unsigned_short()
        self.recordSpecificField = input_stream.read_unsigned_int()


class EntityType(object):
    """Identifies the type of Entity"""

    def __init__(self, entityKind=0, domain=0, country=0, category=0, subcategory=0, specific=0, extra=0):
        """ Initializer for EntityType"""
        self.entityKind = entityKind
        """ Kind of entity"""
        self.domain = domain
        """ Domain of entity (air, surface, subsurface, space, etc)"""
        self.country = country
        """ country to which the design of the entity is attributed"""
        self.category = category
        """ category of entity"""
        self.subcategory = subcategory
        """ subcategory of entity"""
        self.specific = specific
        """ specific info based on subcategory field. Renamed from specific because that is a reserved word in SQL."""
        self.extra = extra

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.entityKind)
        output_stream.write_unsigned_byte(self.domain)
        output_stream.write_unsigned_short(self.country)
        output_stream.write_unsigned_byte(self.category)
        output_stream.write_unsigned_byte(self.subcategory)
        output_stream.write_unsigned_byte(self.specific)
        output_stream.write_unsigned_byte(self.extra)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.entityKind = input_stream.read_unsigned_byte()
        self.domain = input_stream.read_unsigned_byte()
        self.country = input_stream.read_unsigned_short()
        self.category = input_stream.read_unsigned_byte()
        self.subcategory = input_stream.read_unsigned_byte()
        self.specific = input_stream.read_unsigned_byte()
        self.extra = input_stream.read_unsigned_byte()


class Munition(object):
    """An entity's munition (e.g., bomb, missile) information shall be represented by one or more Munition records. For each type or location of munition, this record shall specify the type, location, quantity and status of munitions that an entity contains. Section 6.2.60 """

    def __init__(self):
        """ Initializer for Munition"""
        self.munitionType = EntityType()
        """  This field shall identify the entity type of the munition. See section 6.2.30."""
        self.station = 0
        """ the station or launcher to which the munition is assigned. See Annex I"""
        self.quantity = 0
        """ the quantity remaining of this munition."""
        self.munitionStatus = 0
        """  the status of the munition. It shall be represented by an 8-bit enumeration. """
        self.padding = 0
        """ padding """

    def serialize(self, output_stream):
        """serialize the class """
        self.munitionType.serialize(output_stream)
        output_stream.write_unsigned_int(self.station)
        output_stream.write_unsigned_short(self.quantity)
        output_stream.write_unsigned_byte(self.munitionStatus)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.munitionType.parse(input_stream)
        self.station = input_stream.read_unsigned_int()
        self.quantity = input_stream.read_unsigned_short()
        self.munitionStatus = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class StandardVariableSpecification(object):
    """Does not work, and causes failure in anything it is embedded in. Section 6.2.83"""

    def __init__(self):
        """ Initializer for StandardVariableSpecification"""
        self.numberOfStandardVariableRecords = 0
        """ Number of static variable records"""
        self.standardVariables = []
        """ variable length list of standard variables, The class type and length here are WRONG and will cause the incorrect serialization of any class in whihc it is embedded."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(len(self.standardVariables))
        for anObj in self.standardVariables:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.numberOfStandardVariableRecords = input_stream.read_unsigned_short()
        for idx in range(0, self.numberOfStandardVariableRecords):
            element = null()
            element.parse(input_stream)
            self.standardVariables.append(element)


class Vector2Float(object):
    """Two floating point values, x, y"""

    def __init__(self):
        """ Initializer for Vector2Float"""
        self.x = 0
        """ X value"""
        self.y = 0
        """ y Value"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.x)
        output_stream.write_float(self.y)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.x = input_stream.read_float()
        self.y = input_stream.read_float()


class Environment(object):
    """Incomplete environment record requires hand coding to fix. Section 6.2.31.1"""

    def __init__(self):
        """ Initializer for Environment"""
        self.environmentType = 0
        """ type"""
        self.length = 0
        """ length, in bits, of the record"""
        self.index = 0
        """ identifies the sequntially numbered record index"""
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.environmentType)
        output_stream.write_unsigned_short(self.length)
        output_stream.write_unsigned_byte(self.index)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.environmentType = input_stream.read_unsigned_int()
        self.length = input_stream.read_unsigned_short()
        self.index = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class AcousticEmitter(object):
    """ information about a specific UA emmtter. Section 6.2.2."""

    def __init__(self):
        """ Initializer for AcousticEmitter"""
        self.acousticSystemName = 0
        """ the system for a particular UA emitter, and an enumeration"""
        self.acousticFunction = 0
        """ The function of the acoustic system"""
        self.acousticIDNumber = 0
        """ The UA emitter identification number relative to a specific system"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.acousticSystemName)
        output_stream.write_unsigned_byte(self.acousticFunction)
        output_stream.write_unsigned_byte(self.acousticIDNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.acousticSystemName = input_stream.read_unsigned_short()
        self.acousticFunction = input_stream.read_unsigned_byte()
        self.acousticIDNumber = input_stream.read_unsigned_byte()


class AngularVelocityVector(object):
    """Angular velocity measured in radians per second out each of the entity's own coordinate axes. Order of measurement is angular velocity around the x, y, and z axis of the entity. The positive direction is determined by the right hand rule. Section 6.2.7"""

    def __init__(self):
        """ Initializer for AngularVelocityVector"""
        self.x = 0
        """ velocity about the x axis"""
        self.y = 0
        """ velocity about the y axis"""
        self.z = 0
        """ velocity about the zaxis"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.x)
        output_stream.write_float(self.y)
        output_stream.write_float(self.z)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.x = input_stream.read_float()
        self.y = input_stream.read_float()
        self.z = input_stream.read_float()


class AggregateMarking(object):
    """Specifies the character set used in the first byte, followed by up to 31 characters of text data. Section 6.2.4. """

    def __init__(self):
        """ Initializer for AggregateMarking"""
        self.characterSet = 0
        """ The character set"""
        self.characters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        """ The characters"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.characterSet)
        for idx in range(0, 31):
            output_stream.write_unsigned_byte(self.characters[idx])

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.characterSet = input_stream.read_unsigned_byte()
        self.characters = [0] * 31
        for idx in range(0, 31):
            val = input_stream.read_unsigned_byte()

            self.characters[idx] = val


class DataFilterRecord(object):
    """identify which of the optional data fields are contained in the Minefield Data PDU or requested in the Minefield Query PDU. This is a 32-bit record. For each field, true denotes that the data is requested or present and false denotes that the data is neither requested nor present. Section 6.2.16"""

    def __init__(self):
        """ Initializer for DataFilterRecord"""
        self.bitFlags = 0
        """ Bitflags field"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.bitFlags)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.bitFlags = input_stream.read_unsigned_int()


class IntercomIdentifier(object):
    """Unique designation of an attached or unattached intercom in an event or exercirse. Section 6.2.48"""

    def __init__(self):
        """ Initializer for IntercomIdentifier"""
        self.siteNumber = 0
        self.applicationNumber = 0
        self.referenceNumber = 0
        self.intercomNumber = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.siteNumber)
        output_stream.write_unsigned_short(self.applicationNumber)
        output_stream.write_unsigned_short(self.referenceNumber)
        output_stream.write_unsigned_short(self.intercomNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.siteNumber = input_stream.read_unsigned_short()
        self.applicationNumber = input_stream.read_unsigned_short()
        self.referenceNumber = input_stream.read_unsigned_short()
        self.intercomNumber = input_stream.read_unsigned_short()


class StorageFuel(object):
    """Information about an entity's engine fuel. Section 6.2.84."""

    def __init__(self):
        """ Initializer for StorageFuel"""
        self.fuelQuantity = 0
        """ Fuel quantity, units specified by next field"""
        self.fuelMeasurementUnits = 0
        """ Units in which the fuel is measured"""
        self.fuelType = 0
        """ Type of fuel"""
        self.fuelLocation = 0
        """ Location of fuel as related to entity. See section 14 of EBV document"""
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.fuelQuantity)
        output_stream.write_unsigned_byte(self.fuelMeasurementUnits)
        output_stream.write_unsigned_byte(self.fuelType)
        output_stream.write_unsigned_byte(self.fuelLocation)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.fuelQuantity = input_stream.read_unsigned_int()
        self.fuelMeasurementUnits = input_stream.read_unsigned_byte()
        self.fuelType = input_stream.read_unsigned_byte()
        self.fuelLocation = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class Sensor(object):
    """An entity's sensor information.  Section 6.2.77."""

    def __init__(self):
        """ Initializer for Sensor"""
        self.sensorTypeSource = 0
        """  the source of the Sensor Type field """
        self.sensorOnOffStatus = 0
        """ the on/off status of the sensor"""
        self.sensorType = 0
        """ the sensor type and shall be represented by a 16-bit enumeration. """
        self.station = 0
        """  the station to which the sensor is assigned. A zero value shall indi- cate that this Sensor record is not associated with any particular station and represents the total quan- tity of this sensor for this entity. If this field is non-zero, it shall either reference an attached part or an articulated part"""
        self.quantity = 0
        """ quantity of the sensor """
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.sensorTypeSource)
        output_stream.write_unsigned_byte(self.sensorOnOffStatus)
        output_stream.write_unsigned_short(self.sensorType)
        output_stream.write_unsigned_int(self.station)
        output_stream.write_unsigned_short(self.quantity)
        output_stream.write_unsigned_short(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.sensorTypeSource = input_stream.read_unsigned_byte()
        self.sensorOnOffStatus = input_stream.read_unsigned_byte()
        self.sensorType = input_stream.read_unsigned_short()
        self.station = input_stream.read_unsigned_int()
        self.quantity = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_short()


class MunitionReload(object):
    """indicate weapons (munitions) previously communicated via the Munition record. Section 6.2.61 """

    def __init__(self):
        """ Initializer for MunitionReload"""
        self.munitionType = EntityType()
        """  This field shall identify the entity type of the munition. See section 6.2.30."""
        self.station = 0
        """ the station or launcher to which the munition is assigned. See Annex I"""
        self.standardQuantity = 0
        """ the standard quantity of this munition type normally loaded at this station/launcher if a station/launcher is specified."""
        self.maximumQuantity = 0
        """ the maximum quantity of this munition type that this station/launcher is capable of holding when a station/launcher is specified """
        self.standardQuantityReloadTime = 0
        """ numer of seconds of sim time required to reload the std qty"""
        self.maximumQuantityReloadTime = 0
        """ the number of seconds of sim time required to reload the max possible quantity"""

    def serialize(self, output_stream):
        """serialize the class """
        self.munitionType.serialize(output_stream)
        output_stream.write_unsigned_int(self.station)
        output_stream.write_unsigned_short(self.standardQuantity)
        output_stream.write_unsigned_short(self.maximumQuantity)
        output_stream.write_unsigned_int(self.standardQuantityReloadTime)
        output_stream.write_unsigned_int(self.maximumQuantityReloadTime)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.munitionType.parse(input_stream)
        self.station = input_stream.read_unsigned_int()
        self.standardQuantity = input_stream.read_unsigned_short()
        self.maximumQuantity = input_stream.read_unsigned_short()
        self.standardQuantityReloadTime = input_stream.read_unsigned_int()
        self.maximumQuantityReloadTime = input_stream.read_unsigned_int()


class StorageFuelReload(object):
    """For each type or location of Storage Fuel, this record shall specify the type, location, fuel measure- ment units, reload quantity and maximum quantity for storage fuel either for the whole entity or a specific storage fuel location (tank). Section 6.2.85."""

    def __init__(self):
        """ Initializer for StorageFuelReload"""
        self.standardQuantity = 0
        """  the standard quantity of this fuel type normally loaded at this station/launcher if a station/launcher is specified. If the Station/Launcher field is set to zero, then this is the total quantity of this fuel type that would be present in a standard reload of all appli- cable stations/launchers associated with this entity."""
        self.maximumQuantity = 0
        """ the maximum quantity of this fuel type that this sta- tion/launcher is capable of holding when a station/launcher is specified. This would be the value used when a maximum reload was desired to be set for this station/launcher. If the Station/launcher field is set to zero, then this is the maximum quantity of this fuel type that would be present on this entity at all stations/launchers that can accept this fuel type."""
        self.standardQuantityReloadTime = 0
        """ the seconds normally required to reload the standard quantity of this fuel type at this specific station/launcher. When the Station/Launcher field is set to zero, this shall be the time it takes to perform a standard quantity reload of this fuel type at all applicable stations/launchers for this entity."""
        self.maximumQuantityReloadTime = 0
        """ the seconds normally required to reload the maximum possible quantity of this fuel type at this station/launcher. When the Station/Launcher field is set to zero, this shall be the time it takes to perform a maximum quantity load/reload of this fuel type at all applicable stations/launchers for this entity."""
        self.fuelMeasurementUnits = 0
        """ the fuel measurement units. Enumeration"""
        self.fuelType = 0
        """ Fuel type. Enumeration"""
        self.fuelLocation = 0
        """ Location of fuel as related to entity. See section 14 of EBV document"""
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.standardQuantity)
        output_stream.write_unsigned_int(self.maximumQuantity)
        output_stream.write_unsigned_byte(self.standardQuantityReloadTime)
        output_stream.write_unsigned_byte(self.maximumQuantityReloadTime)
        output_stream.write_unsigned_byte(self.fuelMeasurementUnits)
        output_stream.write_unsigned_byte(self.fuelType)
        output_stream.write_unsigned_byte(self.fuelLocation)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.standardQuantity = input_stream.read_unsigned_int()
        self.maximumQuantity = input_stream.read_unsigned_int()
        self.standardQuantityReloadTime = input_stream.read_unsigned_byte()
        self.maximumQuantityReloadTime = input_stream.read_unsigned_byte()
        self.fuelMeasurementUnits = input_stream.read_unsigned_byte()
        self.fuelType = input_stream.read_unsigned_byte()
        self.fuelLocation = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class ExpendableReload(object):
    """An entity's expendable (chaff, flares, etc) information. Section 6.2.37"""

    def __init__(self):
        """ Initializer for ExpendableReload"""
        self.expendable = EntityType()
        """ Type of expendable"""
        self.station = 0
        self.standardQuantity = 0
        self.maximumQuantity = 0
        self.standardQuantityReloadTime = 0
        self.maximumQuantityReloadTime = 0

    def serialize(self, output_stream):
        """serialize the class """
        self.expendable.serialize(output_stream)
        output_stream.write_unsigned_int(self.station)
        output_stream.write_unsigned_short(self.standardQuantity)
        output_stream.write_unsigned_short(self.maximumQuantity)
        output_stream.write_unsigned_int(self.standardQuantityReloadTime)
        output_stream.write_unsigned_int(self.maximumQuantityReloadTime)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.expendable.parse(input_stream)
        self.station = input_stream.read_unsigned_int()
        self.standardQuantity = input_stream.read_unsigned_short()
        self.maximumQuantity = input_stream.read_unsigned_short()
        self.standardQuantityReloadTime = input_stream.read_unsigned_int()
        self.maximumQuantityReloadTime = input_stream.read_unsigned_int()


class EntityIdentifier(object):
    """Entity Identifier. Unique ID for entities in the world. Consists of an simulation address and a entity number. Section 6.2.28."""

    def __init__(self):
        """ Initializer for EntityIdentifier"""
        self.simulationAddress = SimulationAddress()
        """ Site and application IDs"""
        self.entityNumber = 0
        """ Entity number"""

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.entityNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.entityNumber = input_stream.read_unsigned_short()


class DirectedEnergyTargetEnergyDeposition(object):
    """DE energy depostion properties for a target entity. Section 6.2.20.4"""

    def __init__(self):
        """ Initializer for DirectedEnergyTargetEnergyDeposition"""
        self.targetEntityID = EntityID()
        """ Unique ID of the target entity."""
        self.padding = 0
        """ padding"""
        self.peakIrradiance = 0
        """ Peak irrandiance"""

    def serialize(self, output_stream):
        """serialize the class """
        self.targetEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding)
        output_stream.write_float(self.peakIrradiance)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.targetEntityID.parse(input_stream)
        self.padding = input_stream.read_unsigned_short()
        self.peakIrradiance = input_stream.read_float()


class EntityID(object):
    """more laconically named EntityIdentifier"""

    def __init__(self):
        """ Initializer for EntityID"""
        self.siteID = 0
        """ Site ID"""
        self.applicationID = 0
        """ application number ID"""
        self.entityID = 0
        """ Entity number ID"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.siteID)
        output_stream.write_unsigned_short(self.applicationID)
        output_stream.write_unsigned_short(self.entityID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.siteID = input_stream.read_unsigned_short()
        self.applicationID = input_stream.read_unsigned_short()
        self.entityID = input_stream.read_unsigned_short()


class EngineFuelReload(object):
    """For each type or location of engine fuell, this record specifies the type, location, fuel measurement units, and reload quantity and maximum quantity. Section 6.2.25."""

    def __init__(self):
        """ Initializer for EngineFuelReload"""
        self.standardQuantity = 0
        """ standard quantity of fuel loaded"""
        self.maximumQuantity = 0
        """ maximum quantity of fuel loaded"""
        self.standardQuantityReloadTime = 0
        """ seconds normally required to to reload standard qty"""
        self.maximumQuantityReloadTime = 0
        """ seconds normally required to to reload maximum qty"""
        self.fuelMeasurmentUnits = 0
        """ Units of measure"""
        self.fuelLocation = 0
        """ fuel  location as related to the entity"""
        self.padding = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.standardQuantity)
        output_stream.write_unsigned_int(self.maximumQuantity)
        output_stream.write_unsigned_int(self.standardQuantityReloadTime)
        output_stream.write_unsigned_int(self.maximumQuantityReloadTime)
        output_stream.write_unsigned_byte(self.fuelMeasurmentUnits)
        output_stream.write_unsigned_byte(self.fuelLocation)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.standardQuantity = input_stream.read_unsigned_int()
        self.maximumQuantity = input_stream.read_unsigned_int()
        self.standardQuantityReloadTime = input_stream.read_unsigned_int()
        self.maximumQuantityReloadTime = input_stream.read_unsigned_int()
        self.fuelMeasurmentUnits = input_stream.read_unsigned_byte()
        self.fuelLocation = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class UnattachedIdentifier(object):
    """The unique designation of one or more unattached radios in an event or exercise Section 6.2.91"""

    def __init__(self):
        """ Initializer for UnattachedIdentifier"""
        self.simulationAddress = SimulationAddress()
        """ See 6.2.79"""
        self.referenceNumber = 0
        """ Reference number"""

    def serialize(self, output_stream):
        """serialize the class """
        self.simulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.referenceNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.simulationAddress.parse(input_stream)
        self.referenceNumber = input_stream.read_unsigned_short()


class EntityTypeVP(object):
    """Association or disassociation of two entities.  Section 6.2.94.5"""

    def __init__(self):
        """ Initializer for EntityTypeVP"""
        self.recordType = 3
        """ the identification of the Variable Parameter record. Enumeration from EBV"""
        self.changeIndicator = 0
        """ Indicates if this VP has changed since last issuance"""
        self.entityType = EntityType()
        """ """
        self.padding = 0
        """ padding"""
        self.padding1 = 0
        """ padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.recordType)
        output_stream.write_unsigned_byte(self.changeIndicator)
        self.entityType.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding)
        output_stream.write_unsigned_int(self.padding1)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_byte()
        self.changeIndicator = input_stream.read_unsigned_byte()
        self.entityType.parse(input_stream)
        self.padding = input_stream.read_unsigned_short()
        self.padding1 = input_stream.read_unsigned_int()


class BeamStatus(object):
    """Information related to the status of a beam. This is contained in the beam status field of the electromagnitec emission PDU. The first bit determines whether the beam is active (0) or deactivated (1). Section 6.2.12."""

    def __init__(self):
        """ Initializer for BeamStatus"""
        self.beamState = 0
        """ First bit zero means beam is active, first bit = 1 means deactivated. The rest is padding."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.beamState)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.beamState = input_stream.read_unsigned_byte()


class EnvironmentGeneral(object):
    """ Information about a geometry, a state associated with a geometry, a bounding volume, or an associated entity ID. NOTE: this class requires hand coding. 6.2.31"""

    def __init__(self):
        """ Initializer for EnvironmentGeneral"""
        self.environmentType = 0
        """ Record type"""
        self.length = 0
        """ length, in bits"""
        self.index = 0
        """ Identify the sequentially numbered record index"""
        self.padding1 = 0
        """ padding"""
        self.geometry = 0
        """ Geometry or state record"""
        self.padding2 = 0
        """ padding to bring the total size up to a 64 bit boundry"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.environmentType)
        output_stream.write_unsigned_byte(self.length)
        output_stream.write_unsigned_byte(self.index)
        output_stream.write_unsigned_byte(self.padding1)
        output_stream.write_unsigned_byte(self.geometry)
        output_stream.write_unsigned_byte(self.padding2)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.environmentType = input_stream.read_unsigned_int()
        self.length = input_stream.read_unsigned_byte()
        self.index = input_stream.read_unsigned_byte()
        self.padding1 = input_stream.read_unsigned_byte()
        self.geometry = input_stream.read_unsigned_byte()
        self.padding2 = input_stream.read_unsigned_byte()


class Vector3Double(object):
    """Three double precision floating point values, x, y, and z. Used for world coordinates Section 6.2.97."""

    def __init__(self):
        """ Initializer for Vector3Double"""
        self.x = 0
        """ X value"""
        self.y = 0
        """ y Value"""
        self.z = 0
        """ Z value"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_double(self.x)
        output_stream.write_double(self.y)
        output_stream.write_double(self.z)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.x = input_stream.read_double()
        self.y = input_stream.read_double()
        self.z = input_stream.read_double()


class GridAxis(object):
    """Grid axis record for fixed data. Section 6.2.41"""

    def __init__(self):
        """ Initializer for GridAxis"""
        self.domainInitialXi = 0
        """ coordinate of the grid origin or initial value"""
        self.domainFinalXi = 0
        """ coordinate of the endpoint or final value"""
        self.domainPointsXi = 0
        """ The number of grid points along the Xi domain axis for the enviornmental state data"""
        self.interleafFactor = 0
        """ interleaf factor along the domain axis."""
        self.axisType = 0
        """ type of grid axis"""
        self.numberOfPointsOnXiAxis = 0
        """ Number of grid locations along Xi axis"""
        self.initialIndex = 0
        """ initial grid point for the current pdu"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_double(self.domainInitialXi)
        output_stream.write_double(self.domainFinalXi)
        output_stream.write_unsigned_short(self.domainPointsXi)
        output_stream.write_unsigned_byte(self.interleafFactor)
        output_stream.write_unsigned_byte(self.axisType)
        output_stream.write_unsigned_short(self.numberOfPointsOnXiAxis)
        output_stream.write_unsigned_short(self.initialIndex)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.domainInitialXi = input_stream.read_double()
        self.domainFinalXi = input_stream.read_double()
        self.domainPointsXi = input_stream.read_unsigned_short()
        self.interleafFactor = input_stream.read_unsigned_byte()
        self.axisType = input_stream.read_unsigned_byte()
        self.numberOfPointsOnXiAxis = input_stream.read_unsigned_short()
        self.initialIndex = input_stream.read_unsigned_short()


class RecordSpecification(object):
    """This record shall specify the number of record sets contained in the Record Specification record and the record details. Section 6.2.73."""

    def __init__(self):
        """ Initializer for RecordSpecification"""
        self.numberOfRecordSets = 0
        """ The number of record sets"""
        self.recordSets = []
        """ variable length list record specifications."""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(len(self.recordSets))
        for anObj in self.recordSets:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.numberOfRecordSets = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfRecordSets):
            element = null()
            element.parse(input_stream)
            self.recordSets.append(element)


class VariableDatum(object):
    """the variable datum type, the datum length, and the value for that variable datum type. NOT COMPLETE. Section 6.2.93"""

    def __init__(self):
        """ Initializer for VariableDatum"""
        self.variableDatumID = 0
        """ Type of variable datum to be transmitted. 32 bit enumeration defined in EBV"""
        self.variableDatumLength = 0
        """ Length, IN BITS, of the variable datum."""
        self.variableData = []
        """ Variable datum. This can be any number of bits long, depending on the datum."""

    def datumPaddingSizeInBits(self):
        padding = 0
        remainder = self.variableDatumLength % 64
        if remainder != 0:
            padding = 64 - remainder
        return padding

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_int(self.variableDatumID)
        output_stream.write_unsigned_int(self.variableDatumLength)
        for x in range(self.variableDatumLength // 8):  # length is in bits
            output_stream.write_byte(self.variableData[x])

        # send padding
        for x in range(self.datumPaddingSizeInBits() // 8):
            output_stream.write_byte(0)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.variableDatumID = input_stream.read_unsigned_int()
        self.variableDatumLength = input_stream.read_unsigned_int()
        for x in range(self.variableDatumLength // 8):  # length is in bits
            self.variableData.append(input_stream.read_byte())

        # Skip over padding
        # "This field shall be padded at the end to make the length a multiple of 64-bits."
        for x in range(self.datumPaddingSizeInBits() // 8):
            input_stream.read_byte()


class EventIdentifierLiveEntity(object):
    """Identifies an event in the world. Use this format for ONLY the LiveEntityPdu. Section 6.2.34."""

    def __init__(self):
        """ Initializer for EventIdentifierLiveEntity"""
        self.siteNumber = 0
        self.applicationNumber = 0
        self.eventNumber = 0

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.siteNumber)
        output_stream.write_unsigned_byte(self.applicationNumber)
        output_stream.write_unsigned_short(self.eventNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.siteNumber = input_stream.read_unsigned_byte()
        self.applicationNumber = input_stream.read_unsigned_byte()
        self.eventNumber = input_stream.read_unsigned_short()


class PduHeader(object):
    """Not used. The PDU Header Record is directly incoroporated into the PDU class. Here for completness only. Section 6.2.66"""

    def __init__(self):
        """ Initializer for PduHeader"""
        self.protocolVersion = 7
        """ The version of the protocol. 5=DIS-1995, 6=DIS-1998, 7=DIS-2009."""
        self.exerciseID = 0
        """ Exercise ID"""
        self.pduType = 0
        """ Type of pdu, unique for each PDU class"""
        self.protocolFamily = 0
        """ value that refers to the protocol family, eg SimulationManagement, etc"""
        self.timestamp = 0
        """ Timestamp value"""
        self.pduLength = 0
        """ Length, in bytes, of the PDU. Changed name from length to avoid use of Hibernate QL reserved word."""
        self.pduStatus = 0
        """ PDU Status Record. Described in 6.2.67. This field is not present in earlier DIS versions """
        self.padding = 0
        """ zero filled array of padding"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.protocolVersion)
        output_stream.write_unsigned_byte(self.exerciseID)
        output_stream.write_unsigned_byte(self.pduType)
        output_stream.write_unsigned_byte(self.protocolFamily)
        output_stream.write_unsigned_int(self.timestamp)
        output_stream.write_unsigned_byte(self.pduLength)
        output_stream.write_unsigned_short(self.pduStatus)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.protocolVersion = input_stream.read_unsigned_byte()
        self.exerciseID = input_stream.read_unsigned_byte()
        self.pduType = input_stream.read_unsigned_byte()
        self.protocolFamily = input_stream.read_unsigned_byte()
        self.timestamp = input_stream.read_unsigned_int()
        self.pduLength = input_stream.read_unsigned_byte()
        self.pduStatus = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_byte()


class PduSuperclass(object):
    """The superclass for all PDUs, including classic and Live Entity (LE) PDUs. This incorporates the PduHeader record, section 7.2.2"""

    def __init__(self):
        """ Initializer for PduSuperclass"""
        self.protocolVersion = 7
        """ The version of the protocol. 5=DIS-1995, 6=DIS-1998, 7=DIS-2009."""
        self.exerciseID = 0
        """ Exercise ID"""
        self.pduType = 0
        """ Type of pdu, unique for each PDU class"""
        self.protocolFamily = 0
        """ value that refers to the protocol family, eg SimulationManagement, et"""
        self.timestamp = 0
        """ Timestamp value"""
        self.length = 0
        """ Length, in bytes, of the PDU"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.protocolVersion)
        output_stream.write_unsigned_byte(self.exerciseID)
        output_stream.write_unsigned_byte(self.pduType)
        output_stream.write_unsigned_byte(self.protocolFamily)
        output_stream.write_unsigned_int(self.timestamp)
        output_stream.write_unsigned_short(self.length)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.protocolVersion = input_stream.read_unsigned_byte()
        self.exerciseID = input_stream.read_unsigned_byte()
        self.pduType = input_stream.read_unsigned_byte()
        self.protocolFamily = input_stream.read_unsigned_byte()
        self.timestamp = input_stream.read_unsigned_int()
        self.length = input_stream.read_unsigned_short()


class CommunicationsNodeID(object):
    """Identity of a communications node. Section 6.2.48.4"""

    def __init__(self):
        """ Initializer for CommunicationsNodeID"""
        self.entityID = EntityID()
        self.elementID = 0

    def serialize(self, output_stream):
        """serialize the class """
        self.entityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.elementID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.entityID.parse(input_stream)
        self.elementID = input_stream.read_unsigned_short()


class ExpendableDescriptor(object):
    """Burst of chaff or expendible device. Section 6.2.19.4"""

    def __init__(self):
        """ Initializer for ExpendableDescriptor"""
        self.expendableType = EntityType()
        """ Type of the object that exploded"""
        self.padding = 0
        """ Padding"""

    def serialize(self, output_stream):
        """serialize the class """
        self.expendableType.serialize(output_stream)
        output_stream.write_long(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.expendableType.parse(input_stream)
        self.padding = input_stream.read_long()


class PropulsionSystemData(object):
    """contains information describing the propulsion systems of the entity. This information shall be provided for each active propulsion system defined. Section 6.2.68"""

    def __init__(self):
        """ Initializer for PropulsionSystemData"""
        self.powerSetting = 0
        """ powerSetting"""
        self.engineRpm = 0
        """ engine RPMs"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_float(self.powerSetting)
        output_stream.write_float(self.engineRpm)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.powerSetting = input_stream.read_float()
        self.engineRpm = input_stream.read_float()


class LiveEntityIdentifier(object):
    """The unique designation of each entity in an event or exercise that is contained in a Live Entity PDU. Section 6.2.54 """

    def __init__(self):
        """ Initializer for LiveEntityIdentifier"""
        self.liveSimulationAddress = LiveSimulationAddress()
        """ Live Simulation Address record (see 6.2.54) """
        self.entityNumber = 0
        """ Live entity number """

    def serialize(self, output_stream):
        """serialize the class """
        self.liveSimulationAddress.serialize(output_stream)
        output_stream.write_unsigned_short(self.entityNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.liveSimulationAddress.parse(input_stream)
        self.entityNumber = input_stream.read_unsigned_short()


class SeparationVP(object):
    """Physical separation of an entity from another entity.  Section 6.2.94.6"""

    def __init__(self):
        """ Initializer for SeparationVP"""
        self.recordType = 2
        """ the identification of the Variable Parameter record. Enumeration from EBV"""
        self.reasonForSeparation = 0
        """ Reason for separation. EBV"""
        self.preEntityIndicator = 0
        """ Whether the entity existed prior to separation EBV"""
        self.padding1 = 0
        """ padding"""
        self.parentEntityID = EntityID()
        """ ID of parent"""
        self.padding2 = 0
        """ padding"""
        self.stationLocation = 0
        """ Station separated from"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.recordType)
        output_stream.write_unsigned_byte(self.reasonForSeparation)
        output_stream.write_unsigned_byte(self.preEntityIndicator)
        output_stream.write_unsigned_byte(self.padding1)
        self.parentEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding2)
        output_stream.write_unsigned_int(self.stationLocation)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.recordType = input_stream.read_unsigned_byte()
        self.reasonForSeparation = input_stream.read_unsigned_byte()
        self.preEntityIndicator = input_stream.read_unsigned_byte()
        self.padding1 = input_stream.read_unsigned_byte()
        self.parentEntityID.parse(input_stream)
        self.padding2 = input_stream.read_unsigned_short()
        self.stationLocation = input_stream.read_unsigned_int()


class EmitterSystem(object):
    """This field shall specify information about a particular emitter system. Section 6.2.23."""

    def __init__(self):
        """ Initializer for EmitterSystem"""
        self.emitterName = 0
        """ Name of the emitter, 16 bit enumeration"""
        self.emitterFunction = 0
        """ function of the emitter, 8 bit enumeration"""
        self.emitterIDNumber = 0
        """ emitter ID, 8 bit enumeration"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_short(self.emitterName)
        output_stream.write_unsigned_byte(self.emitterFunction)
        output_stream.write_unsigned_byte(self.emitterIDNumber)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.emitterName = input_stream.read_unsigned_short()
        self.emitterFunction = input_stream.read_unsigned_byte()
        self.emitterIDNumber = input_stream.read_unsigned_byte()


class PduStatus(object):
    """PDU Status. These are a series of bit fields. Represented here as just a byte. Section 6.2.67"""

    def __init__(self):
        """ Initializer for PduStatus"""
        self.pduStatus = 0
        """ Bit fields. The semantics of the bit fields depend on the PDU type"""

    def serialize(self, output_stream):
        """serialize the class """
        output_stream.write_unsigned_byte(self.pduStatus)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        self.pduStatus = input_stream.read_unsigned_byte()


class LiveEntityPdu(PduSuperclass):
    """The live entity PDUs have a header with some different field names, but the same length. Section 9.3.2"""

    def __init__(self):
        """ Initializer for LiveEntityPdu"""
        super(LiveEntityPdu, self).__init__()
        self.subprotocolNumber = 0
        """ Subprotocol used to decode the PDU. Section 13 of EBV."""
        self.padding = 0
        """ zero-filled array of padding"""

    def serialize(self, output_stream):
        """serialize the class """
        super(LiveEntityPdu, self).serialize(output_stream)
        output_stream.write_unsigned_short(self.subprotocolNumber)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(LiveEntityPdu, self).parse(input_stream)
        self.subprotocolNumber = input_stream.read_unsigned_short()
        self.padding = input_stream.read_unsigned_byte()


class Pdu(PduSuperclass):
    """Adds some fields to the the classic PDU"""

    def __init__(self):
        """ Initializer for Pdu"""
        super(Pdu, self).__init__()
        self.pduStatus = 0
        """ PDU Status Record. Described in 6.2.67. This field is not present in earlier DIS versions """
        self.padding = 0
        """ zero-filled array of padding"""

    def serialize(self, output_stream):
        """serialize the class """
        super(Pdu, self).serialize(output_stream)
        output_stream.write_unsigned_byte(self.pduStatus)
        output_stream.write_unsigned_byte(self.padding)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(Pdu, self).parse(input_stream)
        self.pduStatus = input_stream.read_unsigned_byte()
        self.padding = input_stream.read_unsigned_byte()


class EntityInformationFamilyPdu(Pdu):
    """Section 5.3.3. Common superclass for EntityState, Collision, collision-elastic, and entity state update PDUs. This should be abstract. COMPLETE"""

    def __init__(self):
        """ Initializer for EntityInformationFamilyPdu"""
        super(EntityInformationFamilyPdu, self).__init__()
        self.protocolFamily = 1
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(EntityInformationFamilyPdu, self).serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(EntityInformationFamilyPdu, self).parse(input_stream)


class LogisticsFamilyPdu(Pdu):
    """ Abstract superclass for logistics PDUs. Section 7.4 COMPLETE"""

    def __init__(self):
        """ Initializer for LogisticsFamilyPdu"""
        super(LogisticsFamilyPdu, self).__init__()
        self.protocolFamily = 3
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(LogisticsFamilyPdu, self).serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(LogisticsFamilyPdu, self).parse(input_stream)


class EntityStateUpdatePdu(EntityInformationFamilyPdu):
    """Nonstatic information about a particular entity may be communicated by issuing an Entity State Update PDU. Section 7.2.5. COMPLETE"""

    def __init__(self):
        """ Initializer for EntityStateUpdatePdu"""
        super(EntityStateUpdatePdu, self).__init__()
        self.entityID = EntityID()
        """ This field shall identify the entity issuing the PDU, and shall be represented by an Entity Identifier record (see 6.2.28)."""
        self.padding1 = 0
        """ Padding"""
        self.numberOfVariableParameters = 0
        """ This field shall specify the number of variable parameters present. This field shall be represented by an 8-bit unsigned integer (see Annex I)."""
        self.entityLinearVelocity = Vector3Float()
        """ This field shall specify an entitys linear velocity. The coordinate system for an entitys linear velocity depends on the dead reckoning algorithm used. This field shall be represented by a Linear Velocity Vector record [see 6.2.95 item c)])."""
        self.entityLocation = Vector3Double()
        """ This field shall specify an entitys physical location in the simulated world and shall be represented by a World Coordinates record (see 6.2.97)."""
        self.entityOrientation = EulerAngles()
        """ This field shall specify an entitys orientation and shall be represented by an Euler Angles record (see 6.2.33)."""
        self.entityAppearance = 0
        """ This field shall specify the dynamic changes to the entitys appearance attributes. This field shall be represented by an Entity Appearance record (see 6.2.26)."""
        self.variableParameters = []
        """ This field shall specify the parameter values for each Variable Parameter record that is included (see 6.2.93 and Annex I)."""
        self.pduType = 67
        """ initialize value """
        self.protocolFamily = 1
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(EntityStateUpdatePdu, self).serialize(output_stream)
        self.entityID.serialize(output_stream)
        output_stream.write_byte(self.padding1)
        output_stream.write_unsigned_byte(len(self.variableParameters))
        self.entityLinearVelocity.serialize(output_stream)
        self.entityLocation.serialize(output_stream)
        self.entityOrientation.serialize(output_stream)
        output_stream.write_unsigned_int(self.entityAppearance)
        for anObj in self.variableParameters:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(EntityStateUpdatePdu, self).parse(input_stream)
        self.entityID.parse(input_stream)
        self.padding1 = input_stream.read_byte()
        self.numberOfVariableParameters = input_stream.read_unsigned_byte()
        self.entityLinearVelocity.parse(input_stream)
        self.entityLocation.parse(input_stream)
        self.entityOrientation.parse(input_stream)
        self.entityAppearance = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfVariableParameters):
            element = VariableParameter()
            element.parse(input_stream)
            self.variableParameters.append(element)


class ServiceRequestPdu(LogisticsFamilyPdu):
    """Service Request PDU shall be used to communicate information associated with                            one entity requesting a service from another). Section 7.4.2 COMPLETE"""

    def __init__(self):
        """ Initializer for ServiceRequestPdu"""
        super(ServiceRequestPdu, self).__init__()
        self.requestingEntityID = EntityID()
        """ Entity that is requesting service (see 6.2.28), Section 7.4.2"""
        self.servicingEntityID = EntityID()
        """ Entity that is providing the service (see 6.2.28), Section 7.4.2"""
        self.serviceTypeRequested = 0
        """ Type of service requested, Section 7.4.2"""
        self.numberOfSupplyTypes = 0
        """ How many requested, Section 7.4.2"""
        self.serviceRequestPadding = 0
        """ padding"""
        self.supplies = []
        self.pduType = 5
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ServiceRequestPdu, self).serialize(output_stream)
        self.requestingEntityID.serialize(output_stream)
        self.servicingEntityID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.serviceTypeRequested)
        output_stream.write_unsigned_byte(len(self.supplies))
        output_stream.write_short(self.serviceRequestPadding)
        for anObj in self.supplies:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ServiceRequestPdu, self).parse(input_stream)
        self.requestingEntityID.parse(input_stream)
        self.servicingEntityID.parse(input_stream)
        self.serviceTypeRequested = input_stream.read_unsigned_byte()
        self.numberOfSupplyTypes = input_stream.read_unsigned_byte()
        self.serviceRequestPadding = input_stream.read_short()
        for idx in range(0, self.numberOfSupplyTypes):
            element = null()
            element.parse(input_stream)
            self.supplies.append(element)


class RepairCompletePdu(LogisticsFamilyPdu):
    """Section 7.4.6. Service Request PDU is received and repair is complete. COMPLETE"""

    def __init__(self):
        """ Initializer for RepairCompletePdu"""
        super(RepairCompletePdu, self).__init__()
        self.receivingEntityID = EntityID()
        """ Entity that is receiving service.  See 6.2.28"""
        self.repairingEntityID = EntityID()
        """ Entity that is supplying.  See 6.2.28"""
        self.repair = 0
        """ Enumeration for type of repair.  See 6.2.74"""
        self.padding4 = 0
        """ padding, number prevents conflict with superclass ivar name"""
        self.pduType = 9
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(RepairCompletePdu, self).serialize(output_stream)
        self.receivingEntityID.serialize(output_stream)
        self.repairingEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.repair)
        output_stream.write_short(self.padding4)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(RepairCompletePdu, self).parse(input_stream)
        self.receivingEntityID.parse(input_stream)
        self.repairingEntityID.parse(input_stream)
        self.repair = input_stream.read_unsigned_short()
        self.padding4 = input_stream.read_short()


class SyntheticEnvironmentFamilyPdu(Pdu):
    """Section 5.3.11: Abstract superclass for synthetic environment PDUs"""

    def __init__(self):
        """ Initializer for SyntheticEnvironmentFamilyPdu"""
        super(SyntheticEnvironmentFamilyPdu, self).__init__()
        self.protocolFamily = 9
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(SyntheticEnvironmentFamilyPdu, self).serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(SyntheticEnvironmentFamilyPdu, self).parse(input_stream)


class CollisionPdu(EntityInformationFamilyPdu):
    """Section 7.2.3 Collisions between entities shall be communicated by issuing a Collision PDU. COMPLETE"""

    def __init__(self):
        """ Initializer for CollisionPdu"""
        super(CollisionPdu, self).__init__()
        self.issuingEntityID = EntityID()
        """ This field shall identify the entity that is issuing the PDU, and shall be represented by an Entity Identifier record (see 6.2.28)."""
        self.collidingEntityID = EntityID()
        """ This field shall identify the entity that has collided with the issuing entity (see 5.3.3.4). This field shall be represented by an Entity Identifier record (see 6.2.28)."""
        self.eventID = EventIdentifier()
        """ This field shall contain an identification generated by the issuing simulation application to associate related collision events. This field shall be represented by an Event Identifier record (see 6.2.34)."""
        self.collisionType = 0
        """ This field shall identify the type of collision. The Collision Type field shall be represented by an 8-bit record of enumerations"""
        self.pad = 0
        """ some padding"""
        self.velocity = Vector3Float()
        """ This field shall contain the velocity (at the time the collision is detected) of the issuing entity. The velocity shall be represented in world coordinates. This field shall be represented by the Linear Velocity Vector record [see 6.2.95 item c)]."""
        self.mass = 0
        """ This field shall contain the mass of the issuing entity, and shall be represented by a 32-bit floating point number representing kilograms."""
        self.location = Vector3Float()
        """ This field shall specify the location of the collision with respect to the entity with which the issuing entity collided. The Location field shall be represented by an Entity Coordinate Vector record [see 6.2.95 item a)]."""
        self.pduType = 4
        """ initialize value """
        self.protocolFamily = 1
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(CollisionPdu, self).serialize(output_stream)
        self.issuingEntityID.serialize(output_stream)
        self.collidingEntityID.serialize(output_stream)
        self.eventID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.collisionType)
        output_stream.write_byte(self.pad)
        self.velocity.serialize(output_stream)
        output_stream.write_float(self.mass)
        self.location.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(CollisionPdu, self).parse(input_stream)
        self.issuingEntityID.parse(input_stream)
        self.collidingEntityID.parse(input_stream)
        self.eventID.parse(input_stream)
        self.collisionType = input_stream.read_unsigned_byte()
        self.pad = input_stream.read_byte()
        self.velocity.parse(input_stream)
        self.mass = input_stream.read_float()
        self.location.parse(input_stream)


class RepairResponsePdu(LogisticsFamilyPdu):
    """Section 7.4.7. Sent after repair complete PDU. COMPLETE"""

    def __init__(self):
        """ Initializer for RepairResponsePdu"""
        super(RepairResponsePdu, self).__init__()
        self.receivingEntityID = EntityID()
        """ Entity that requested repairs.  See 6.2.28"""
        self.repairingEntityID = EntityID()
        """ Entity that is repairing.  See 6.2.28"""
        self.repairResult = 0
        """ Result of repair operation"""
        self.padding1 = 0
        """ padding"""
        self.padding2 = 0
        """ padding"""
        self.pduType = 10
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(RepairResponsePdu, self).serialize(output_stream)
        self.receivingEntityID.serialize(output_stream)
        self.repairingEntityID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.repairResult)
        output_stream.write_short(self.padding1)
        output_stream.write_byte(self.padding2)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(RepairResponsePdu, self).parse(input_stream)
        self.receivingEntityID.parse(input_stream)
        self.repairingEntityID.parse(input_stream)
        self.repairResult = input_stream.read_unsigned_byte()
        self.padding1 = input_stream.read_short()
        self.padding2 = input_stream.read_byte()


class SimulationManagementFamilyPdu(Pdu):
    """Section 7.5 Abstract superclass for PDUs relating to the simulation itself. COMPLETE"""

    def __init__(self):
        """ Initializer for SimulationManagementFamilyPdu"""
        super(SimulationManagementFamilyPdu, self).__init__()
        self.originatingEntityID = EntityID()
        """ Entity that is sending message"""
        self.receivingEntityID = EntityID()
        """ Entity that is intended to receive message"""
        self.protocolFamily = 5
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(SimulationManagementFamilyPdu, self).serialize(output_stream)
        self.originatingEntityID.serialize(output_stream)
        self.receivingEntityID.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(SimulationManagementFamilyPdu, self).parse(input_stream)
        self.originatingEntityID.parse(input_stream)
        self.receivingEntityID.parse(input_stream)


class DataQueryPdu(SimulationManagementFamilyPdu):
    """Section 7.5.9. Request for data from an entity. COMPLETE"""

    def __init__(self):
        """ Initializer for DataQueryPdu"""
        super(DataQueryPdu, self).__init__()
        self.requestID = 0
        """ ID of request"""
        self.timeInterval = 0
        """ time issues between issues of Data PDUs. Zero means send once only."""
        self.numberOfFixedDatumRecords = 0
        """ Number of fixed datum records"""
        self.numberOfVariableDatumRecords = 0
        """ Number of variable datum records"""
        self.fixedDatums = []
        """ variable length list of fixed datums"""
        self.variableDatums = []
        """ variable length list of variable length datums"""
        self.pduType = 18
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DataQueryPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.timeInterval)
        output_stream.write_unsigned_int(len(self.fixedDatums))
        output_stream.write_unsigned_int(len(self.variableDatums))
        for anObj in self.fixedDatums:
            anObj.serialize(output_stream)

        for anObj in self.variableDatums:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DataQueryPdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.timeInterval = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatums.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatums.append(element)


class LinearObjectStatePdu(SyntheticEnvironmentFamilyPdu):
    """: Information abut the addition or modification of a synthecic enviroment object that      is anchored to the terrain with a single point and has size or orientation. Section 7.10.5 COMPLETE"""

    def __init__(self):
        """ Initializer for LinearObjectStatePdu"""
        super(LinearObjectStatePdu, self).__init__()
        self.objectID = EntityID()
        """ Object in synthetic environment"""
        self.referencedObjectID = EntityID()
        """ Object with which this point object is associated"""
        self.updateNumber = 0
        """ unique update number of each state transition of an object"""
        self.forceID = 0
        """ force ID"""
        self.numberOfSegments = 0
        """ number of linear segment parameters"""
        self.requesterID = SimulationAddress()
        """ requesterID"""
        self.receivingID = SimulationAddress()
        """ receiver ID"""
        self.objectType = ObjectType()
        """ Object type"""
        self.linearSegmentParameters = []
        """ Linear segment parameters"""
        self.pduType = 44
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(LinearObjectStatePdu, self).serialize(output_stream)
        self.objectID.serialize(output_stream)
        self.referencedObjectID.serialize(output_stream)
        output_stream.write_unsigned_short(self.updateNumber)
        output_stream.write_unsigned_byte(self.forceID)
        output_stream.write_unsigned_byte(len(self.linearSegmentParameters))
        self.requesterID.serialize(output_stream)
        self.receivingID.serialize(output_stream)
        self.objectType.serialize(output_stream)
        for anObj in self.linearSegmentParameters:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(LinearObjectStatePdu, self).parse(input_stream)
        self.objectID.parse(input_stream)
        self.referencedObjectID.parse(input_stream)
        self.updateNumber = input_stream.read_unsigned_short()
        self.forceID = input_stream.read_unsigned_byte()
        self.numberOfSegments = input_stream.read_unsigned_byte()
        self.requesterID.parse(input_stream)
        self.receivingID.parse(input_stream)
        self.objectType.parse(input_stream)
        for idx in range(0, self.numberOfSegments):
            element = null()
            element.parse(input_stream)
            self.linearSegmentParameters.append(element)


class CreateEntityPdu(SimulationManagementFamilyPdu):
    """Section 7.5.2. Create a new entity. COMPLETE"""

    def __init__(self):
        """ Initializer for CreateEntityPdu"""
        super(CreateEntityPdu, self).__init__()
        self.requestID = 0
        """ Identifier for the request.  See 6.2.75"""
        self.pduType = 11
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(CreateEntityPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(CreateEntityPdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()


class RadioCommunicationsFamilyPdu(Pdu):
    """ Abstract superclass for radio communications PDUs. Section 7.7"""

    def __init__(self):
        """ Initializer for RadioCommunicationsFamilyPdu"""
        super(RadioCommunicationsFamilyPdu, self).__init__()
        self.protocolFamily = 4
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(RadioCommunicationsFamilyPdu, self).serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(RadioCommunicationsFamilyPdu, self).parse(input_stream)


class IntercomSignalPdu(RadioCommunicationsFamilyPdu):
    """ Actual transmission of intercome voice data. Section 7.7.5. COMPLETE"""

    def __init__(self):
        """ Initializer for IntercomSignalPdu"""
        super(IntercomSignalPdu, self).__init__()
        self.entityID = EntityID()
        """ entity ID"""
        self.communicationsDeviceID = 0
        """ ID of communications device"""
        self.encodingScheme = 0
        """ encoding scheme"""
        self.tdlType = 0
        """ tactical data link type"""
        self.sampleRate = 0
        """ sample rate"""
        self.dataLength = 0
        """ data length"""
        self.samples = 0
        """ samples"""
        self.data = []
        """ data bytes"""
        self.pduType = 31
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(IntercomSignalPdu, self).serialize(output_stream)
        self.entityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.communicationsDeviceID)
        output_stream.write_unsigned_short(self.encodingScheme)
        output_stream.write_unsigned_short(self.tdlType)
        output_stream.write_unsigned_int(self.sampleRate)
        output_stream.write_unsigned_short(len(self.data))
        output_stream.write_unsigned_short(self.samples)
        for anObj in self.data:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(IntercomSignalPdu, self).parse(input_stream)
        self.entityID.parse(input_stream)
        self.communicationsDeviceID = input_stream.read_unsigned_short()
        self.encodingScheme = input_stream.read_unsigned_short()
        self.tdlType = input_stream.read_unsigned_short()
        self.sampleRate = input_stream.read_unsigned_int()
        self.dataLength = input_stream.read_unsigned_short()
        self.samples = input_stream.read_unsigned_short()
        for idx in range(0, self.dataLength):
            element = null()
            element.parse(input_stream)
            self.data.append(element)


class RemoveEntityPdu(SimulationManagementFamilyPdu):
    """Section 7.5.3 The removal of an entity from an exercise shall be communicated with a Remove Entity PDU. COMPLETE"""

    def __init__(self):
        """ Initializer for RemoveEntityPdu"""
        super(RemoveEntityPdu, self).__init__()
        self.requestID = 0
        """ This field shall identify the specific and unique start/resume request being made by the SM"""
        self.pduType = 12
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(RemoveEntityPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(RemoveEntityPdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()


class ResupplyReceivedPdu(LogisticsFamilyPdu):
    """Section 7.4.4. Receipt of supplies is communicated by issuing Resupply Received PDU. COMPLETE"""

    def __init__(self):
        """ Initializer for ResupplyReceivedPdu"""
        super(ResupplyReceivedPdu, self).__init__()
        self.receivingEntityID = EntityID()
        """ Entity that is receiving service.  Shall be represented by Entity Identifier record (see 6.2.28)"""
        self.supplyingEntityID = EntityID()
        """ Entity that is supplying.  Shall be represented by Entity Identifier record (see 6.2.28)"""
        self.numberOfSupplyTypes = 0
        """ How many supplies are taken by receiving entity"""
        self.padding1 = 0
        """ padding"""
        self.padding2 = 0
        """ padding"""
        self.supplies = []
        """ Type and amount of supplies for each specified supply type.  See 6.2.85 for supply quantity record."""
        self.pduType = 7
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ResupplyReceivedPdu, self).serialize(output_stream)
        self.receivingEntityID.serialize(output_stream)
        self.supplyingEntityID.serialize(output_stream)
        output_stream.write_unsigned_byte(len(self.supplies))
        output_stream.write_short(self.padding1)
        output_stream.write_byte(self.padding2)
        for anObj in self.supplies:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ResupplyReceivedPdu, self).parse(input_stream)
        self.receivingEntityID.parse(input_stream)
        self.supplyingEntityID.parse(input_stream)
        self.numberOfSupplyTypes = input_stream.read_unsigned_byte()
        self.padding1 = input_stream.read_short()
        self.padding2 = input_stream.read_byte()
        for idx in range(0, self.numberOfSupplyTypes):
            element = null()
            element.parse(input_stream)
            self.supplies.append(element)


class WarfareFamilyPdu(Pdu):
    """abstract superclass for fire and detonation pdus that have shared information. Section 7.3 COMPLETE"""

    def __init__(self):
        """ Initializer for WarfareFamilyPdu"""
        super(WarfareFamilyPdu, self).__init__()
        self.firingEntityID = EntityID()
        """ ID of the entity that shot"""
        self.targetEntityID = EntityID()
        """ ID of the entity that is being shot at"""
        self.protocolFamily = 2
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(WarfareFamilyPdu, self).serialize(output_stream)
        self.firingEntityID.serialize(output_stream)
        self.targetEntityID.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(WarfareFamilyPdu, self).parse(input_stream)
        self.firingEntityID.parse(input_stream)
        self.targetEntityID.parse(input_stream)


class CollisionElasticPdu(EntityInformationFamilyPdu):
    """Information about elastic collisions in a DIS exercise shall be communicated using a Collision-Elastic PDU. Section 7.2.4. COMPLETE"""

    def __init__(self):
        """ Initializer for CollisionElasticPdu"""
        super(CollisionElasticPdu, self).__init__()
        self.issuingEntityID = EntityID()
        """ This field shall identify the entity that is issuing the PDU and shall be represented by an Entity Identifier record (see 6.2.28)"""
        self.collidingEntityID = EntityID()
        """ This field shall identify the entity that has collided with the issuing entity. This field shall be a valid identifier of an entity or server capable of responding to the receipt of this Collision-Elastic PDU. This field shall be represented by an Entity Identifier record (see 6.2.28)."""
        self.collisionEventID = EventIdentifier()
        """ This field shall contain an identification generated by the issuing simulation application to associate related collision events. This field shall be represented by an Event Identifier record (see 6.2.34)."""
        self.pad = 0
        """ some padding"""
        self.contactVelocity = Vector3Float()
        """ This field shall contain the velocity at the time the collision is detected at the point the collision is detected. The velocity shall be represented in world coordinates. This field shall be represented by the Linear Velocity Vector record [see 6.2.95 item c)]"""
        self.mass = 0
        """ This field shall contain the mass of the issuing entity and shall be represented by a 32-bit floating point number representing kilograms"""
        self.locationOfImpact = Vector3Float()
        """ This field shall specify the location of the collision with respect to the entity with which the issuing entity collided. This field shall be represented by an Entity Coordinate Vector record [see 6.2.95 item a)]."""
        self.collisionIntermediateResultXX = 0
        """ These six records represent the six independent components of a positive semi-definite matrix formed by pre-multiplying and post-multiplying the tensor of inertia, by the anti-symmetric matrix generated by the moment arm, and shall be represented by 32-bit floating point numbers (see 5.3.4.4)"""
        self.collisionIntermediateResultXY = 0
        """ tensor values"""
        self.collisionIntermediateResultXZ = 0
        """ tensor values"""
        self.collisionIntermediateResultYY = 0
        """ tensor values"""
        self.collisionIntermediateResultYZ = 0
        """ tensor values"""
        self.collisionIntermediateResultZZ = 0
        """ tensor values"""
        self.unitSurfaceNormal = Vector3Float()
        """ This record shall represent the normal vector to the surface at the point of collision detection. The surface normal shall be represented in world coordinates. This field shall be represented by an Entity Coordinate Vector record [see 6.2.95 item a)]."""
        self.coefficientOfRestitution = 0
        """ This field shall represent the degree to which energy is conserved in a collision and shall be represented by a 32-bit floating point number. In addition, it represents a free parameter by which simulation application developers may tune their collision interactions."""
        self.pduType = 66
        """ initialize value """
        self.protocolFamily = 1
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(CollisionElasticPdu, self).serialize(output_stream)
        self.issuingEntityID.serialize(output_stream)
        self.collidingEntityID.serialize(output_stream)
        self.collisionEventID.serialize(output_stream)
        output_stream.write_short(self.pad)
        self.contactVelocity.serialize(output_stream)
        output_stream.write_float(self.mass)
        self.locationOfImpact.serialize(output_stream)
        output_stream.write_float(self.collisionIntermediateResultXX)
        output_stream.write_float(self.collisionIntermediateResultXY)
        output_stream.write_float(self.collisionIntermediateResultXZ)
        output_stream.write_float(self.collisionIntermediateResultYY)
        output_stream.write_float(self.collisionIntermediateResultYZ)
        output_stream.write_float(self.collisionIntermediateResultZZ)
        self.unitSurfaceNormal.serialize(output_stream)
        output_stream.write_float(self.coefficientOfRestitution)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(CollisionElasticPdu, self).parse(input_stream)
        self.issuingEntityID.parse(input_stream)
        self.collidingEntityID.parse(input_stream)
        self.collisionEventID.parse(input_stream)
        self.pad = input_stream.read_short()
        self.contactVelocity.parse(input_stream)
        self.mass = input_stream.read_float()
        self.locationOfImpact.parse(input_stream)
        self.collisionIntermediateResultXX = input_stream.read_float()
        self.collisionIntermediateResultXY = input_stream.read_float()
        self.collisionIntermediateResultXZ = input_stream.read_float()
        self.collisionIntermediateResultYY = input_stream.read_float()
        self.collisionIntermediateResultYZ = input_stream.read_float()
        self.collisionIntermediateResultZZ = input_stream.read_float()
        self.unitSurfaceNormal.parse(input_stream)
        self.coefficientOfRestitution = input_stream.read_float()


class ActionRequestPdu(SimulationManagementFamilyPdu):
    """Section 7.5.7. Request from simulation manager to a managed entity to perform a specified action. COMPLETE"""

    def __init__(self):
        """ Initializer for ActionRequestPdu"""
        super(ActionRequestPdu, self).__init__()
        self.requestID = 0
        """ identifies the request being made by the simulaton manager"""
        self.actionID = 0
        """ identifies the particular action being requested(see Section 7 of SISO-REF-010)."""
        self.numberOfFixedDatumRecords = 0
        """ Number of fixed datum records"""
        self.numberOfVariableDatumRecords = 0
        """ Number of variable datum records"""
        self.fixedDatums = []
        """ variable length list of fixed datums"""
        self.variableDatums = []
        """ variable length list of variable length datums"""
        self.pduType = 16
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ActionRequestPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.actionID)
        output_stream.write_unsigned_int(len(self.fixedDatums))
        output_stream.write_unsigned_int(len(self.variableDatums))
        for anObj in self.fixedDatums:
            anObj.serialize(output_stream)

        for anObj in self.variableDatums:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ActionRequestPdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.actionID = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatums.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatums.append(element)


class AcknowledgePdu(SimulationManagementFamilyPdu):
    """Section 7.5.6. Acknowledge the receipt of a start/resume, stop/freeze, or RemoveEntityPDU. COMPLETE"""

    def __init__(self):
        """ Initializer for AcknowledgePdu"""
        super(AcknowledgePdu, self).__init__()
        self.acknowledgeFlag = 0
        """ type of message being acknowledged"""
        self.responseFlag = 0
        """ Whether or not the receiving entity was able to comply with the request"""
        self.requestID = 0
        """ Request ID that is unique"""
        self.pduType = 15
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(AcknowledgePdu, self).serialize(output_stream)
        output_stream.write_unsigned_short(self.acknowledgeFlag)
        output_stream.write_unsigned_short(self.responseFlag)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(AcknowledgePdu, self).parse(input_stream)
        self.acknowledgeFlag = input_stream.read_unsigned_short()
        self.responseFlag = input_stream.read_unsigned_short()
        self.requestID = input_stream.read_unsigned_int()


class DistributedEmissionsFamilyPdu(Pdu):
    """Section 5.3.7. Electronic Emissions. Abstract superclass for distirubted emissions PDU"""

    def __init__(self):
        """ Initializer for DistributedEmissionsFamilyPdu"""
        super(DistributedEmissionsFamilyPdu, self).__init__()
        self.protocolFamily = 6
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DistributedEmissionsFamilyPdu, self).serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DistributedEmissionsFamilyPdu, self).parse(input_stream)


class SimulationManagementWithReliabilityFamilyPdu(Pdu):
    """Section 5.3.12: Abstract superclass for reliable simulation management PDUs"""

    def __init__(self):
        """ Initializer for SimulationManagementWithReliabilityFamilyPdu"""
        super(SimulationManagementWithReliabilityFamilyPdu, self).__init__()
        self.originatingEntityID = EntityID()
        """ Object originatig the request"""
        self.receivingEntityID = EntityID()
        """ Object with which this point object is associated"""
        self.protocolFamily = 10
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(SimulationManagementWithReliabilityFamilyPdu, self).serialize(output_stream)
        self.originatingEntityID.serialize(output_stream)
        self.receivingEntityID.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(SimulationManagementWithReliabilityFamilyPdu, self).parse(input_stream)
        self.originatingEntityID.parse(input_stream)
        self.receivingEntityID.parse(input_stream)


class ActionRequestReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.6: request from a simulation manager to a managed entity to perform a specified action. COMPLETE"""

    def __init__(self):
        """ Initializer for ActionRequestReliablePdu"""
        super(ActionRequestReliablePdu, self).__init__()
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding"""
        self.pad2 = 0
        """ padding"""
        self.requestID = 0
        """ request ID"""
        self.actionID = 0
        """ request ID"""
        self.numberOfFixedDatumRecords = 0
        """ Fixed datum record count"""
        self.numberOfVariableDatumRecords = 0
        """ variable datum record count"""
        self.fixedDatumRecords = []
        """ Fixed datum records"""
        self.variableDatumRecords = []
        """ Variable datum records"""
        self.pduType = 56
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ActionRequestReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.actionID)
        output_stream.write_unsigned_int(len(self.fixedDatumRecords))
        output_stream.write_unsigned_int(len(self.variableDatumRecords))
        for anObj in self.fixedDatumRecords:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ActionRequestReliablePdu, self).parse(input_stream)
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.requestID = input_stream.read_unsigned_int()
        self.actionID = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumRecords.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumRecords.append(element)


class DesignatorPdu(DistributedEmissionsFamilyPdu):
    """Section 5.3.7.2. Handles designating operations. COMPLETE"""

    def __init__(self):
        """ Initializer for DesignatorPdu"""
        super(DesignatorPdu, self).__init__()
        self.designatingEntityID = EntityID()
        """ ID of the entity designating"""
        self.codeName = 0
        """ This field shall specify a unique emitter database number assigned to  differentiate between otherwise similar or identical emitter beams within an emitter system."""
        self.designatedEntityID = EntityID()
        """ ID of the entity being designated"""
        self.designatorCode = 0
        """ This field shall identify the designator code being used by the designating entity """
        self.designatorPower = 0
        """ This field shall identify the designator output power in watts"""
        self.designatorWavelength = 0
        """ This field shall identify the designator wavelength in units of microns"""
        self.designatorSpotWrtDesignated = Vector3Float()
        """ designtor spot wrt the designated entity"""
        self.designatorSpotLocation = Vector3Double()
        """ designtor spot wrt the designated entity"""
        self.deadReckoningAlgorithm = 0
        """ Dead reckoning algorithm"""
        self.padding1 = 0
        """ padding"""
        self.padding2 = 0
        """ padding"""
        self.entityLinearAcceleration = Vector3Float()
        """ linear accelleration of entity"""
        self.pduType = 24
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DesignatorPdu, self).serialize(output_stream)
        self.designatingEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.codeName)
        self.designatedEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.designatorCode)
        output_stream.write_float(self.designatorPower)
        output_stream.write_float(self.designatorWavelength)
        self.designatorSpotWrtDesignated.serialize(output_stream)
        self.designatorSpotLocation.serialize(output_stream)
        output_stream.write_byte(self.deadReckoningAlgorithm)
        output_stream.write_unsigned_short(self.padding1)
        output_stream.write_byte(self.padding2)
        self.entityLinearAcceleration.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DesignatorPdu, self).parse(input_stream)
        self.designatingEntityID.parse(input_stream)
        self.codeName = input_stream.read_unsigned_short()
        self.designatedEntityID.parse(input_stream)
        self.designatorCode = input_stream.read_unsigned_short()
        self.designatorPower = input_stream.read_float()
        self.designatorWavelength = input_stream.read_float()
        self.designatorSpotWrtDesignated.parse(input_stream)
        self.designatorSpotLocation.parse(input_stream)
        self.deadReckoningAlgorithm = input_stream.read_byte()
        self.padding1 = input_stream.read_unsigned_short()
        self.padding2 = input_stream.read_byte()
        self.entityLinearAcceleration.parse(input_stream)


class StopFreezePdu(SimulationManagementFamilyPdu):
    """Section 7.5.5. Stop or freeze an enity (or exercise). COMPLETE"""

    def __init__(self):
        """ Initializer for StopFreezePdu"""
        super(StopFreezePdu, self).__init__()
        self.realWorldTime = ClockTime()
        """ real-world(UTC) time at which the entity shall stop or freeze in the exercise"""
        self.reason = 0
        """ Reason the simulation was stopped or frozen (see section 7 of SISO-REF-010) represented by an 8-bit enumeration"""
        self.frozenBehavior = 0
        """ Internal behavior of the entity(or simulation) and its appearance while frozen to the other participants"""
        self.padding1 = 0
        """ padding"""
        self.requestID = 0
        """ Request ID that is unique"""
        self.pduType = 14
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(StopFreezePdu, self).serialize(output_stream)
        self.realWorldTime.serialize(output_stream)
        output_stream.write_unsigned_byte(self.reason)
        output_stream.write_unsigned_byte(self.frozenBehavior)
        output_stream.write_short(self.padding1)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(StopFreezePdu, self).parse(input_stream)
        self.realWorldTime.parse(input_stream)
        self.reason = input_stream.read_unsigned_byte()
        self.frozenBehavior = input_stream.read_unsigned_byte()
        self.padding1 = input_stream.read_short()
        self.requestID = input_stream.read_unsigned_int()


class EntityStatePdu(EntityInformationFamilyPdu):
    """Represents the postion and state of one entity in the world. Section 7.2.2. COMPLETE"""

    def __init__(self):
        """ Initializer for EntityStatePdu"""
        super(EntityStatePdu, self).__init__()
        self.entityID = EntityID()
        """ Unique ID for an entity that is tied to this state information"""
        self.forceId = 0
        """ What force this entity is affiliated with, eg red, blue, neutral, etc"""
        self.numberOfVariableParameters = 0
        """ How many variable parameters are in the variable length list. In earlier versions of DIS these were known as articulation parameters"""
        self.entityType = EntityType()
        """ Describes the type of entity in the world"""
        self.alternativeEntityType = EntityType()
        self.entityLinearVelocity = Vector3Float()
        """ Describes the speed of the entity in the world"""
        self.entityLocation = Vector3Double()
        """ describes the location of the entity in the world"""
        self.entityOrientation = EulerAngles()
        """ describes the orientation of the entity, in euler angles"""
        self.entityAppearance = 0
        """ a series of bit flags that are used to help draw the entity, such as smoking, on fire, etc."""
        self.deadReckoningParameters = DeadReckoningParameters()
        """ parameters used for dead reckoning"""
        self.marking = EntityMarking()
        """ characters that can be used for debugging, or to draw unique strings on the side of entities in the world"""
        self.capabilities = 0
        """ a series of bit flags"""
        self.variableParameters = []
        """ variable length list of variable parameters. In earlier DIS versions this was articulation parameters."""
        self.pduType = 1
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(EntityStatePdu, self).serialize(output_stream)
        self.entityID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.forceId)
        output_stream.write_unsigned_byte(len(self.variableParameters))
        self.entityType.serialize(output_stream)
        self.alternativeEntityType.serialize(output_stream)
        self.entityLinearVelocity.serialize(output_stream)
        self.entityLocation.serialize(output_stream)
        self.entityOrientation.serialize(output_stream)
        output_stream.write_unsigned_int(self.entityAppearance)
        self.deadReckoningParameters.serialize(output_stream)
        self.marking.serialize(output_stream)
        output_stream.write_unsigned_int(self.capabilities)
        for anObj in self.variableParameters:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(EntityStatePdu, self).parse(input_stream)
        self.entityID.parse(input_stream)
        self.forceId = input_stream.read_unsigned_byte()
        self.numberOfVariableParameters = input_stream.read_unsigned_byte()
        self.entityType.parse(input_stream)
        self.alternativeEntityType.parse(input_stream)
        self.entityLinearVelocity.parse(input_stream)
        self.entityLocation.parse(input_stream)
        self.entityOrientation.parse(input_stream)
        self.entityAppearance = input_stream.read_unsigned_int()
        self.deadReckoningParameters.parse(input_stream)
        self.marking.parse(input_stream)
        self.capabilities = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfVariableParameters):
            element = VariableParameter()
            element.parse(input_stream)
            self.variableParameters.append(element)


class EntityManagementFamilyPdu(Pdu):
    """ Managment of grouping of PDUs, and more. Section 7.8"""

    def __init__(self):
        """ Initializer for EntityManagementFamilyPdu"""
        super(EntityManagementFamilyPdu, self).__init__()
        self.protocolFamily = 7
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(EntityManagementFamilyPdu, self).serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(EntityManagementFamilyPdu, self).parse(input_stream)


class StartResumePdu(SimulationManagementFamilyPdu):
    """Section 7.5.4. Start or resume an exercise. COMPLETE"""

    def __init__(self):
        """ Initializer for StartResumePdu"""
        super(StartResumePdu, self).__init__()
        self.realWorldTime = ClockTime()
        """ This field shall specify the real-world time (UTC) at which the entity is to start/resume in the exercise. This information shall be used by the participating simulation applications to start/resume an exercise synchronously. This field shall be represented by a Clock Time record (see 6.2.16)."""
        self.simulationTime = ClockTime()
        """ The reference time within a simulation exercise. This time is established ahead of time by simulation management and is common to all participants in a particular exercise. Simulation time may be either Absolute Time or Relative Time. This field shall be represented by a Clock Time record (see 6.2.16)"""
        self.requestID = 0
        """ Identifier for the specific and unique start/resume request"""
        self.pduType = 13
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(StartResumePdu, self).serialize(output_stream)
        self.realWorldTime.serialize(output_stream)
        self.simulationTime.serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(StartResumePdu, self).parse(input_stream)
        self.realWorldTime.parse(input_stream)
        self.simulationTime.parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()


class TransmitterPdu(RadioCommunicationsFamilyPdu):
    """Detailed information about a radio transmitter. This PDU requires manually written code to complete, since the modulation parameters are of variable length. Section 7.7.2 UNFINISHED"""

    def __init__(self):
        """ Initializer for TransmitterPdu"""
        super(TransmitterPdu, self).__init__()
        self.radioReferenceID = EntityID()
        """ ID of the entitythat is the source of the communication"""
        self.radioNumber = 0
        """ particular radio within an entity"""
        self.radioEntityType = EntityType()
        """ Type of radio"""
        self.transmitState = 0
        """ transmit state"""
        self.inputSource = 0
        """ input source"""
        self.variableTransmitterParameterCount = 0
        """ count field"""
        self.antennaLocation = Vector3Double()
        """ Location of antenna"""
        self.relativeAntennaLocation = Vector3Float()
        """ relative location of antenna"""
        self.antennaPatternType = 0
        """ antenna pattern type"""
        self.antennaPatternCount = 0
        """ atenna pattern length"""
        self.frequency = 0
        """ frequency"""
        self.transmitFrequencyBandwidth = 0
        """ transmit frequency Bandwidth"""
        self.power = 0
        """ transmission power"""
        self.modulationType = ModulationType()
        """ modulation"""
        self.cryptoSystem = 0
        """ crypto system enumeration"""
        self.cryptoKeyId = 0
        """ crypto system key identifer"""
        self.modulationParameterCount = 0
        """ how many modulation parameters we have"""
        self.padding2 = 0
        """ padding2"""
        self.padding3 = 0
        """ padding3"""
        self.modulationParametersList = []
        """ variable length list of modulation parameters"""
        self.antennaPatternList = []
        """ variable length list of antenna pattern records"""
        self.pduType = 25
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(TransmitterPdu, self).serialize(output_stream)
        self.radioReferenceID.serialize(output_stream)
        output_stream.write_unsigned_short(self.radioNumber)
        self.radioEntityType.serialize(output_stream)
        output_stream.write_unsigned_byte(self.transmitState)
        output_stream.write_unsigned_byte(self.inputSource)
        output_stream.write_unsigned_short(self.variableTransmitterParameterCount)
        self.antennaLocation.serialize(output_stream)
        self.relativeAntennaLocation.serialize(output_stream)
        output_stream.write_unsigned_short(self.antennaPatternType)
        output_stream.write_unsigned_short(len(self.antennaPatternList))
        output_stream.write_long(self.frequency)
        output_stream.write_float(self.transmitFrequencyBandwidth)
        output_stream.write_float(self.power)
        self.modulationType.serialize(output_stream)
        output_stream.write_unsigned_short(self.cryptoSystem)
        output_stream.write_unsigned_short(self.cryptoKeyId)
        output_stream.write_unsigned_byte(len(self.modulationParametersList))
        output_stream.write_unsigned_short(self.padding2)
        output_stream.write_unsigned_byte(self.padding3)
        for anObj in self.modulationParametersList:
            anObj.serialize(output_stream)

        for anObj in self.antennaPatternList:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(TransmitterPdu, self).parse(input_stream)
        self.radioReferenceID.parse(input_stream)
        self.radioNumber = input_stream.read_unsigned_short()
        self.radioEntityType.parse(input_stream)
        self.transmitState = input_stream.read_unsigned_byte()
        self.inputSource = input_stream.read_unsigned_byte()
        self.variableTransmitterParameterCount = input_stream.read_unsigned_short()
        self.antennaLocation.parse(input_stream)
        self.relativeAntennaLocation.parse(input_stream)
        self.antennaPatternType = input_stream.read_unsigned_short()
        self.antennaPatternCount = input_stream.read_unsigned_short()
        self.frequency = input_stream.read_long()
        self.transmitFrequencyBandwidth = input_stream.read_float()
        self.power = input_stream.read_float()
        self.modulationType.parse(input_stream)
        self.cryptoSystem = input_stream.read_unsigned_short()
        self.cryptoKeyId = input_stream.read_unsigned_short()
        self.modulationParameterCount = input_stream.read_unsigned_byte()
        self.padding2 = input_stream.read_unsigned_short()
        self.padding3 = input_stream.read_unsigned_byte()

        """ Vendor product MACE from BattleSpace Inc, only uses 1 byte per modulation param """
        """ SISO Spec dictates it should be 2 bytes """
        """ Instead of dumpping the packet we can make an assumption that some vendors use 1 byte per param """
        """ Although we will still send out 2 bytes per param as per spec """
        endsize = self.antennaPatternCount * 39
        mod_bytes = 2

        if (self.modulationParameterCount > 0):
            curr = input_stream.stream.tell()
            remaining = input_stream.stream.read(None)
            mod_bytes = (len(remaining) - endsize) / self.modulationParameterCount
            input_stream.stream.seek(curr, 0)

        if (mod_bytes > 2):
            print("Malformed Packet")
        else:
            for idx in range(0, self.modulationParameterCount):
                if mod_bytes == 2:
                    element = input_stream.read_unsigned_short()
                else:
                    element = input_stream.read_unsigned_byte()
                self.modulationParametersList.append(element)
            for idx in range(0, self.antennaPatternCount):
                element = BeamAntennaPattern()
                element.parse(input_stream)
                self.antennaPatternList.append(element)


class ElectronicEmissionsPdu(DistributedEmissionsFamilyPdu):
    """Section 5.3.7.1. Information about active electronic warfare (EW) emissions and active EW countermeasures shall be communicated using an Electromagnetic Emission PDU."""

    def __init__(self):
        """ Initializer for ElectronicEmissionsPdu"""
        super(ElectronicEmissionsPdu, self).__init__()
        self.emittingEntityID = EntityID()
        """ ID of the entity emitting"""
        self.eventID = EventIdentifier()
        """ ID of event"""
        self.stateUpdateIndicator = 0
        """ This field shall be used to indicate if the data in the PDU represents a state update or just data that has changed since issuance of the last Electromagnetic Emission PDU [relative to the identified entity and emission system(s)]."""
        self.numberOfSystems = 0
        """ This field shall specify the number of emission systems being described in the current PDU."""
        self.systems = []
        """ Electronic emmissions systems THIS IS WRONG. It has the WRONG class type and will cause problems in any marshalling."""
        self.pduType = 23
        """ initialize value """
        self.paddingForEmissionsPdu = 0
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ElectronicEmissionsPdu, self).serialize(output_stream)
        self.emittingEntityID.serialize(output_stream)
        self.eventID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.stateUpdateIndicator)
        output_stream.write_unsigned_byte(len(self.systems))
        output_stream.write_unsigned_short(self.paddingForEmissionsPdu)

        for anObj in self.systems:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ElectronicEmissionsPdu, self).parse(input_stream)
        self.emittingEntityID.parse(input_stream)
        self.eventID.parse(input_stream)
        self.stateUpdateIndicator = input_stream.read_unsigned_byte()
        self.numberOfSystems = input_stream.read_unsigned_byte()
        self.paddingForEmissionsPdu = input_stream.read_unsigned_short()

        for idx in range(0, self.numberOfSystems):
            element = EmissionSystemRecord()
            element.parse(input_stream)
            self.systems.append(element)


class EmissionSystemBeamRecord():
    def __init__(self):
        self.beamDataLength = 0
        self.beamIDNumber = 0
        self.beamParameterIndex = 0
        self.fundamentalParameterData = EEFundamentalParameterData()
        self.beamFunction = 0
        self.numberOfTargetsInTrackJam = 0
        self.highDensityTrackJam = 0
        self.jammingModeSequence = 0
        self.trackJamRecords = []

    def serialize(self, output_stream):
        output_stream.write_unsigned_byte(self.beamDataLength)
        output_stream.write_unsigned_byte(self.beamIDNumber)
        output_stream.write_unsigned_short(self.beamParameterIndex)
        self.fundamentalParameterData.serialize(output_stream)
        output_stream.write_unsigned_byte(self.beamFunction)
        output_stream.write_unsigned_byte(self.numberOfTargetsInTrackJam)
        output_stream.write_unsigned_byte(self.highDensityTrackJam)
        output_stream.write_unsigned_byte(0)  # 8 bit padding
        output_stream.write_unsigned_int(self.jammingModeSequence)

        for anObj in self.trackJamRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        self.beamDataLength = input_stream.read_unsigned_byte()
        self.beamIDNumber = input_stream.read_unsigned_byte()
        self.beamParameterIndex = input_stream.read_unsigned_short()
        self.fundamentalParameterData.parse(input_stream)
        self.beamFunction = input_stream.read_unsigned_byte()
        self.numberOfTargetsInTrackJam = input_stream.read_unsigned_byte()
        self.highDensityTrackJam = input_stream.read_unsigned_byte()
        input_stream.read_unsigned_byte()  # 8 bit padding
        self.jammingModeSequence = input_stream.read_unsigned_int()

        for idx in range(0, self.numberOfTargetsInTrackJam):
            element = TrackJamData()
            element.parse(input_stream)
            self.trackJamRecords.append(element)


class EmissionSystemRecord():
    def __init__(self):
        self.systemDataLength = 0
        """  this field shall specify the length of this emitter system's data in 32-bit words."""
        self.numberOfBeams = 0
        """ the number of beams being described in the current PDU for the emitter system being described. """
        self.paddingForEmissionsPdu = 0
        """ padding"""
        self.emitterSystem = EmitterSystem()
        """  information about a particular emitter system and shall be represented by an Emitter System record (see 6.2.23)."""
        self.location = Vector3Float()
        """ the location of the antenna beam source with respect to the emitting entity's coordinate system. This location shall be the origin of the emitter coordinate system that shall have the same orientation as the entity coordinate system. This field shall be represented by an Entity Coordinate Vector record see 6.2.95 """
        self.beamRecords = []

    def serialize(self, output_stream):
        output_stream.write_unsigned_byte(self.systemDataLength)
        output_stream.write_unsigned_byte(self.numberOfBeams)
        output_stream.write_unsigned_short(0)  # 16 bit padding
        self.emitterSystem.serialize(output_stream)
        self.location.serialize(output_stream)
        for anObj in self.beamRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        self.systemDataLength = input_stream.read_unsigned_byte()
        self.numberOfBeams = input_stream.read_unsigned_byte()
        input_stream.read_unsigned_short()  # 16 bit padding
        self.emitterSystem.parse(input_stream)
        self.location.parse(input_stream)
        for idx in range(0, self.numberOfBeams):
            element = EmissionSystemBeamRecord()
            element.parse(input_stream)
            self.beamRecords.append(element)


class ResupplyOfferPdu(LogisticsFamilyPdu):
    """Information used to communicate the offer of supplies by a supplying entity to a receiving entity. Section 7.4.3 COMPLETE"""

    def __init__(self):
        """ Initializer for ResupplyOfferPdu"""
        super(ResupplyOfferPdu, self).__init__()
        self.receivingEntityID = EntityID()
        """ Field identifies the Entity and respective Entity Record ID that is receiving service (see 6.2.28), Section 7.4.3"""
        self.supplyingEntityID = EntityID()
        """ Identifies the Entity and respective Entity ID Record that is supplying  (see 6.2.28), Section 7.4.3"""
        self.numberOfSupplyTypes = 0
        """ How many supplies types are being offered, Section 7.4.3"""
        self.padding1 = 0
        """ padding"""
        self.padding2 = 0
        """ padding"""
        self.supplies = []
        """ A Reord that Specifies the type of supply and the amount of that supply for each of the supply types in numberOfSupplyTypes (see 6.2.85), Section 7.4.3"""
        self.pduType = 6
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ResupplyOfferPdu, self).serialize(output_stream)
        self.receivingEntityID.serialize(output_stream)
        self.supplyingEntityID.serialize(output_stream)
        output_stream.write_unsigned_byte(len(self.supplies))
        output_stream.write_byte(self.padding1)
        output_stream.write_short(self.padding2)
        for anObj in self.supplies:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ResupplyOfferPdu, self).parse(input_stream)
        self.receivingEntityID.parse(input_stream)
        self.supplyingEntityID.parse(input_stream)
        self.numberOfSupplyTypes = input_stream.read_unsigned_byte()
        self.padding1 = input_stream.read_byte()
        self.padding2 = input_stream.read_short()
        for idx in range(0, self.numberOfSupplyTypes):
            element = null()
            element.parse(input_stream)
            self.supplies.append(element)


class AttributePdu(EntityInformationFamilyPdu):
    """Information about individual attributes for a particular entity, other object, or event may be communicated using an Attribute PDU. The Attribute PDU shall not be used to exchange data available in any other PDU except where explicitly mentioned in the PDU issuance instructions within this standard. See 5.3.6 for the information requirements and issuance and receipt rules for this PDU. Section 7.2.6. INCOMPLETE"""

    def __init__(self):
        """ Initializer for AttributePdu"""
        super(AttributePdu, self).__init__()
        self.originatingSimulationAddress = SimulationAddress()
        """ This field shall identify the simulation issuing the Attribute PDU. It shall be represented by a Simulation Address record (see 6.2.79)."""
        self.padding1 = 0
        """ Padding"""
        self.padding2 = 0
        """ Padding"""
        self.attributeRecordPduType = 0
        """ This field shall represent the type of the PDU that is being extended or updated, if applicable. It shall be represented by an 8-bit enumeration."""
        self.attributeRecordProtocolVersion = 0
        """ This field shall indicate the Protocol Version associated with the Attribute Record PDU Type. It shall be represented by an 8-bit enumeration."""
        self.masterAttributeRecordType = 0
        """ This field shall contain the Attribute record type of the Attribute records in the PDU if they all have the same Attribute record type. It shall be represented by a 32-bit enumeration."""
        self.actionCode = 0
        """ This field shall identify the action code applicable to this Attribute PDU. The Action Code shall apply to all Attribute records contained in the PDU. It shall be represented by an 8-bit enumeration."""
        self.padding3 = 0
        """ Padding"""
        self.numberAttributeRecordSet = 0
        """ This field shall specify the number of Attribute Record Sets that make up the remainder of the PDU. It shall be represented by a 16-bit unsigned integer."""

    def serialize(self, output_stream):
        """serialize the class """
        super(AttributePdu, self).serialize(output_stream)
        self.originatingSimulationAddress.serialize(output_stream)
        output_stream.write_int(self.padding1)
        output_stream.write_short(self.padding2)
        output_stream.write_unsigned_byte(self.attributeRecordPduType)
        output_stream.write_unsigned_byte(self.attributeRecordProtocolVersion)
        output_stream.write_unsigned_int(self.masterAttributeRecordType)
        output_stream.write_unsigned_byte(self.actionCode)
        output_stream.write_byte(self.padding3)
        output_stream.write_unsigned_short(self.numberAttributeRecordSet)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(AttributePdu, self).parse(input_stream)
        self.originatingSimulationAddress.parse(input_stream)
        self.padding1 = input_stream.read_int()
        self.padding2 = input_stream.read_short()
        self.attributeRecordPduType = input_stream.read_unsigned_byte()
        self.attributeRecordProtocolVersion = input_stream.read_unsigned_byte()
        self.masterAttributeRecordType = input_stream.read_unsigned_int()
        self.actionCode = input_stream.read_unsigned_byte()
        self.padding3 = input_stream.read_byte()
        self.numberAttributeRecordSet = input_stream.read_unsigned_short()


class MinefieldFamilyPdu(Pdu):
    """ Abstract superclass for PDUs relating to minefields. Section 7.9"""

    def __init__(self):
        """ Initializer for MinefieldFamilyPdu"""
        super(MinefieldFamilyPdu, self).__init__()
        self.protocolFamily = 8
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(MinefieldFamilyPdu, self).serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(MinefieldFamilyPdu, self).parse(input_stream)


class SetDataReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.9: initializing or chaning internal state information, reliable. Needs manual intervention to fix     padding on variable datums. UNFINISHED"""

    def __init__(self):
        """ Initializer for SetDataReliablePdu"""
        super(SetDataReliablePdu, self).__init__()
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding"""
        self.pad2 = 0
        """ padding"""
        self.requestID = 0
        """ Request ID"""
        self.numberOfFixedDatumRecords = 0
        """ Fixed datum record count"""
        self.numberOfVariableDatumRecords = 0
        """ variable datum record count"""
        self.fixedDatumRecords = []
        """ Fixed datum records"""
        self.variableDatumRecords = []
        """ Variable datum records"""
        self.pduType = 59
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(SetDataReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(len(self.fixedDatumRecords))
        output_stream.write_unsigned_int(len(self.variableDatumRecords))
        for anObj in self.fixedDatumRecords:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(SetDataReliablePdu, self).parse(input_stream)
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.requestID = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumRecords.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumRecords.append(element)


class EventReportPdu(SimulationManagementFamilyPdu):
    """ Reports occurance of a significant event to the simulation manager. Section 7.5.12. COMPLETE"""

    def __init__(self):
        """ Initializer for EventReportPdu"""
        super(EventReportPdu, self).__init__()
        self.eventType = 0
        """ Type of event"""
        self.padding1 = 0
        """ padding"""
        self.numberOfFixedDatumRecords = 0
        """ Number of fixed datum records"""
        self.numberOfVariableDatumRecords = 0
        """ Number of variable datum records"""
        self.fixedDatums = []
        """ variable length list of fixed datums"""
        self.variableDatums = []
        """ variable length list of variable length datums"""
        self.pduType = 21
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(EventReportPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.eventType)
        output_stream.write_unsigned_int(self.padding1)
        output_stream.write_unsigned_int(len(self.fixedDatums))
        output_stream.write_unsigned_int(len(self.variableDatums))
        for anObj in self.fixedDatums:
            anObj.serialize(output_stream)

        for anObj in self.variableDatums:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(EventReportPdu, self).parse(input_stream)
        self.eventType = input_stream.read_unsigned_int()
        self.padding1 = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatums.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatums.append(element)


class PointObjectStatePdu(SyntheticEnvironmentFamilyPdu):
    """: Inormation abut the addition or modification of a synthecic enviroment object that is anchored to the terrain with a single point. Section 7.10.4 COMPLETE"""

    def __init__(self):
        """ Initializer for PointObjectStatePdu"""
        super(PointObjectStatePdu, self).__init__()
        self.objectID = EntityID()
        """ Object in synthetic environment"""
        self.referencedObjectID = EntityID()
        """ Object with which this point object is associated"""
        self.updateNumber = 0
        """ unique update number of each state transition of an object"""
        self.forceID = 0
        """ force ID"""
        self.modifications = 0
        """ modifications"""
        self.objectType = ObjectType()
        """ Object type"""
        self.objectLocation = Vector3Double()
        """ Object location"""
        self.objectOrientation = EulerAngles()
        """ Object orientation"""
        self.objectAppearance = 0
        """ Object apperance"""
        self.requesterID = SimulationAddress()
        """ requesterID"""
        self.receivingID = SimulationAddress()
        """ receiver ID"""
        self.pad2 = 0
        """ padding"""
        self.pduType = 43
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(PointObjectStatePdu, self).serialize(output_stream)
        self.objectID.serialize(output_stream)
        self.referencedObjectID.serialize(output_stream)
        output_stream.write_unsigned_short(self.updateNumber)
        output_stream.write_unsigned_byte(self.forceID)
        output_stream.write_unsigned_byte(self.modifications)
        self.objectType.serialize(output_stream)
        self.objectLocation.serialize(output_stream)
        self.objectOrientation.serialize(output_stream)
        output_stream.write_double(self.objectAppearance)
        self.requesterID.serialize(output_stream)
        self.receivingID.serialize(output_stream)
        output_stream.write_unsigned_int(self.pad2)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(PointObjectStatePdu, self).parse(input_stream)
        self.objectID.parse(input_stream)
        self.referencedObjectID.parse(input_stream)
        self.updateNumber = input_stream.read_unsigned_short()
        self.forceID = input_stream.read_unsigned_byte()
        self.modifications = input_stream.read_unsigned_byte()
        self.objectType.parse(input_stream)
        self.objectLocation.parse(input_stream)
        self.objectOrientation.parse(input_stream)
        self.objectAppearance = input_stream.read_double()
        self.requesterID.parse(input_stream)
        self.receivingID.parse(input_stream)
        self.pad2 = input_stream.read_unsigned_int()


class DataPdu(SimulationManagementFamilyPdu):
    """ Information issued in response to a data query pdu or a set data pdu is communicated using a data pdu. Section 7.5.11 COMPLETE"""

    def __init__(self):
        """ Initializer for DataPdu"""
        super(DataPdu, self).__init__()
        self.requestID = 0
        """ ID of request"""
        self.padding1 = 0
        """ padding"""
        self.numberOfFixedDatumRecords = 0
        """ Number of fixed datum records"""
        self.numberOfVariableDatumRecords = 0
        """ Number of variable datum records"""
        self.fixedDatums = []
        """ variable length list of fixed datums"""
        self.variableDatums = []
        """ variable length list of variable length datums"""
        self.pduType = 20
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DataPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.padding1)
        output_stream.write_unsigned_int(len(self.fixedDatums))
        output_stream.write_unsigned_int(len(self.variableDatums))
        for anObj in self.fixedDatums:
            anObj.serialize(output_stream)

        for anObj in self.variableDatums:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DataPdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.padding1 = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatums.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatums.append(element)


class FastEntityStatePdu(EntityInformationFamilyPdu):
    """Represents the postion and state of one entity in the world. This is identical in function to entity state pdu, but generates less garbage to collect in the Java world. Section 7.2.2. COMPLETE"""

    def __init__(self):
        """ Initializer for FastEntityStatePdu"""
        super(FastEntityStatePdu, self).__init__()
        self.site = 0
        """ The site ID"""
        self.application = 0
        """ The application ID"""
        self.entity = 0
        """ the entity ID"""
        self.forceId = 0
        """ what force this entity is affiliated with, eg red, blue, neutral, etc"""
        self.numberOfVariableParameters = 0
        """ How many variable (nee articulation) parameters are in the variable length list"""
        self.entityKind = 0
        """ Kind of entity"""
        self.domain = 0
        """ Domain of entity (air, surface, subsurface, space, etc)"""
        self.country = 0
        """ country to which the design of the entity is attributed"""
        self.category = 0
        """ category of entity"""
        self.subcategory = 0
        """ subcategory of entity"""
        self.specific = 0
        """ specific info based on subcategory field"""
        self.extra = 0
        self.altEntityKind = 0
        """ Kind of entity"""
        self.altDomain = 0
        """ Domain of entity (air, surface, subsurface, space, etc)"""
        self.altCountry = 0
        """ country to which the design of the entity is attributed"""
        self.altCategory = 0
        """ category of entity"""
        self.altSubcategory = 0
        """ subcategory of entity"""
        self.altSpecific = 0
        """ specific info based on subcategory field"""
        self.altExtra = 0
        self.xVelocity = 0
        """ X velo"""
        self.yVelocity = 0
        """ y Value"""
        self.zVelocity = 0
        """ Z value"""
        self.xLocation = 0
        """ X value"""
        self.yLocation = 0
        """ y Value"""
        self.zLocation = 0
        """ Z value"""
        self.psi = 0
        self.theta = 0
        self.phi = 0
        self.entityAppearance = 0
        """ a series of bit flags that are used to help draw the entity, such as smoking, on fire, etc."""
        self.deadReckoningAlgorithm = 0
        """ enumeration of what dead reckoning algorighm to use"""
        self.otherParameters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        """ other parameters to use in the dead reckoning algorithm"""
        self.xAcceleration = 0
        """ X value"""
        self.yAcceleration = 0
        """ y Value"""
        self.zAcceleration = 0
        """ Z value"""
        self.xAngularVelocity = 0
        """ X value"""
        self.yAngularVelocity = 0
        """ y Value"""
        self.zAngularVelocity = 0
        """ Z value"""
        self.marking = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        """ characters that can be used for debugging, or to draw unique strings on the side of entities in the world"""
        self.capabilities = 0
        """ a series of bit flags"""
        self.variableParameters = []
        """ variable length list of variable parameters. In earlier versions of DIS these were known as articulation parameters"""
        self.pduType = 1
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(FastEntityStatePdu, self).serialize(output_stream)
        output_stream.write_unsigned_short(self.site)
        output_stream.write_unsigned_short(self.application)
        output_stream.write_unsigned_short(self.entity)
        output_stream.write_unsigned_byte(self.forceId)
        output_stream.write_byte(len(self.variableParameters))
        output_stream.write_unsigned_byte(self.entityKind)
        output_stream.write_unsigned_byte(self.domain)
        output_stream.write_unsigned_short(self.country)
        output_stream.write_unsigned_byte(self.category)
        output_stream.write_unsigned_byte(self.subcategory)
        output_stream.write_unsigned_byte(self.specific)
        output_stream.write_unsigned_byte(self.extra)
        output_stream.write_unsigned_byte(self.altEntityKind)
        output_stream.write_unsigned_byte(self.altDomain)
        output_stream.write_unsigned_short(self.altCountry)
        output_stream.write_unsigned_byte(self.altCategory)
        output_stream.write_unsigned_byte(self.altSubcategory)
        output_stream.write_unsigned_byte(self.altSpecific)
        output_stream.write_unsigned_byte(self.altExtra)
        output_stream.write_float(self.xVelocity)
        output_stream.write_float(self.yVelocity)
        output_stream.write_float(self.zVelocity)
        output_stream.write_double(self.xLocation)
        output_stream.write_double(self.yLocation)
        output_stream.write_double(self.zLocation)
        output_stream.write_float(self.psi)
        output_stream.write_float(self.theta)
        output_stream.write_float(self.phi)
        output_stream.write_int(self.entityAppearance)
        output_stream.write_unsigned_byte(self.deadReckoningAlgorithm)
        for idx in range(0, 15):
            output_stream.write_byte(self.otherParameters[idx])

        output_stream.write_float(self.xAcceleration)
        output_stream.write_float(self.yAcceleration)
        output_stream.write_float(self.zAcceleration)
        output_stream.write_float(self.xAngularVelocity)
        output_stream.write_float(self.yAngularVelocity)
        output_stream.write_float(self.zAngularVelocity)
        for idx in range(0, 12):
            output_stream.write_byte(self.marking[idx])

        output_stream.write_int(self.capabilities)
        for anObj in self.variableParameters:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(FastEntityStatePdu, self).parse(input_stream)
        self.site = input_stream.read_unsigned_short()
        self.application = input_stream.read_unsigned_short()
        self.entity = input_stream.read_unsigned_short()
        self.forceId = input_stream.read_unsigned_byte()
        self.numberOfVariableParameters = input_stream.read_byte()
        self.entityKind = input_stream.read_unsigned_byte()
        self.domain = input_stream.read_unsigned_byte()
        self.country = input_stream.read_unsigned_short()
        self.category = input_stream.read_unsigned_byte()
        self.subcategory = input_stream.read_unsigned_byte()
        self.specific = input_stream.read_unsigned_byte()
        self.extra = input_stream.read_unsigned_byte()
        self.altEntityKind = input_stream.read_unsigned_byte()
        self.altDomain = input_stream.read_unsigned_byte()
        self.altCountry = input_stream.read_unsigned_short()
        self.altCategory = input_stream.read_unsigned_byte()
        self.altSubcategory = input_stream.read_unsigned_byte()
        self.altSpecific = input_stream.read_unsigned_byte()
        self.altExtra = input_stream.read_unsigned_byte()
        self.xVelocity = input_stream.read_float()
        self.yVelocity = input_stream.read_float()
        self.zVelocity = input_stream.read_float()
        self.xLocation = input_stream.read_double()
        self.yLocation = input_stream.read_double()
        self.zLocation = input_stream.read_double()
        self.psi = input_stream.read_float()
        self.theta = input_stream.read_float()
        self.phi = input_stream.read_float()
        self.entityAppearance = input_stream.read_int()
        self.deadReckoningAlgorithm = input_stream.read_unsigned_byte()
        self.otherParameters = [0] * 15
        for idx in range(0, 15):
            val = input_stream.read_byte()

            self.otherParameters[idx] = val

        self.xAcceleration = input_stream.read_float()
        self.yAcceleration = input_stream.read_float()
        self.zAcceleration = input_stream.read_float()
        self.xAngularVelocity = input_stream.read_float()
        self.yAngularVelocity = input_stream.read_float()
        self.zAngularVelocity = input_stream.read_float()
        self.marking = [0] * 12
        for idx in range(0, 12):
            val = input_stream.read_byte()

            self.marking[idx] = val

        self.capabilities = input_stream.read_int()
        for idx in range(0, self.numberOfVariableParameters):
            element = VariableParameter()
            element.parse(input_stream)
            self.variableParameters.append(element)


class AcknowledgeReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.5: Ack receipt of a start-resume, stop-freeze, create-entity or remove enitty (reliable) pdus. COMPLETE"""

    def __init__(self):
        """ Initializer for AcknowledgeReliablePdu"""
        super(AcknowledgeReliablePdu, self).__init__()
        self.acknowledgeFlag = 0
        """ ack flags"""
        self.responseFlag = 0
        """ response flags"""
        self.requestID = 0
        """ Request ID"""
        self.pduType = 55
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(AcknowledgeReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_short(self.acknowledgeFlag)
        output_stream.write_unsigned_short(self.responseFlag)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(AcknowledgeReliablePdu, self).parse(input_stream)
        self.acknowledgeFlag = input_stream.read_unsigned_short()
        self.responseFlag = input_stream.read_unsigned_short()
        self.requestID = input_stream.read_unsigned_int()


class StartResumeReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.3: Start resume simulation, relaible. COMPLETE"""

    def __init__(self):
        """ Initializer for StartResumeReliablePdu"""
        super(StartResumeReliablePdu, self).__init__()
        self.realWorldTime = ClockTime()
        """ time in real world for this operation to happen"""
        self.simulationTime = ClockTime()
        """ time in simulation for the simulation to resume"""
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding"""
        self.pad2 = 0
        """ padding"""
        self.requestID = 0
        """ Request ID"""
        self.pduType = 53
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(StartResumeReliablePdu, self).serialize(output_stream)
        self.realWorldTime.serialize(output_stream)
        self.simulationTime.serialize(output_stream)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(StartResumeReliablePdu, self).parse(input_stream)
        self.realWorldTime.parse(input_stream)
        self.simulationTime.parse(input_stream)
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.requestID = input_stream.read_unsigned_int()


class ArealObjectStatePdu(SyntheticEnvironmentFamilyPdu):
    """Information about the addition/modification of an oobject that is geometrically anchored to the terrain with a set of three or more points that come to a closure. Section 7.10.6 COMPLETE"""

    def __init__(self):
        """ Initializer for ArealObjectStatePdu"""
        super(ArealObjectStatePdu, self).__init__()
        self.objectID = EntityID()
        """ Object in synthetic environment"""
        self.referencedObjectID = EntityID()
        """ Object with which this point object is associated"""
        self.updateNumber = 0
        """ unique update number of each state transition of an object"""
        self.forceID = 0
        """ force ID"""
        self.modifications = 0
        """ modifications enumeration"""
        self.objectType = EntityType()
        """ Object type"""
        self.specificObjectAppearance = 0
        """ Object appearance"""
        self.generalObjectAppearance = 0
        """ Object appearance"""
        self.numberOfPoints = 0
        """ Number of points"""
        self.requesterID = SimulationAddress()
        """ requesterID"""
        self.receivingID = SimulationAddress()
        """ receiver ID"""
        self.objectLocation = []
        """ location of object"""
        self.pduType = 45
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ArealObjectStatePdu, self).serialize(output_stream)
        self.objectID.serialize(output_stream)
        self.referencedObjectID.serialize(output_stream)
        output_stream.write_unsigned_short(self.updateNumber)
        output_stream.write_unsigned_byte(self.forceID)
        output_stream.write_unsigned_byte(self.modifications)
        self.objectType.serialize(output_stream)
        output_stream.write_unsigned_int(self.specificObjectAppearance)
        output_stream.write_unsigned_short(self.generalObjectAppearance)
        output_stream.write_unsigned_short(len(self.objectLocation))
        self.requesterID.serialize(output_stream)
        self.receivingID.serialize(output_stream)
        for anObj in self.objectLocation:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ArealObjectStatePdu, self).parse(input_stream)
        self.objectID.parse(input_stream)
        self.referencedObjectID.parse(input_stream)
        self.updateNumber = input_stream.read_unsigned_short()
        self.forceID = input_stream.read_unsigned_byte()
        self.modifications = input_stream.read_unsigned_byte()
        self.objectType.parse(input_stream)
        self.specificObjectAppearance = input_stream.read_unsigned_int()
        self.generalObjectAppearance = input_stream.read_unsigned_short()
        self.numberOfPoints = input_stream.read_unsigned_short()
        self.requesterID.parse(input_stream)
        self.receivingID.parse(input_stream)
        for idx in range(0, self.numberOfPoints):
            element = null()
            element.parse(input_stream)
            self.objectLocation.append(element)


class DataQueryReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.8: request for data from an entity. COMPLETE"""

    def __init__(self):
        """ Initializer for DataQueryReliablePdu"""
        super(DataQueryReliablePdu, self).__init__()
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding"""
        self.pad2 = 0
        """ padding"""
        self.requestID = 0
        """ request ID"""
        self.timeInterval = 0
        """ time interval between issuing data query PDUs"""
        self.numberOfFixedDatumRecords = 0
        """ Fixed datum record count"""
        self.numberOfVariableDatumRecords = 0
        """ variable datum record count"""
        self.fixedDatumRecords = []
        """ Fixed datum records"""
        self.variableDatumRecords = []
        """ Variable datum records"""
        self.pduType = 58
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DataQueryReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.timeInterval)
        output_stream.write_unsigned_int(len(self.fixedDatumRecords))
        output_stream.write_unsigned_int(len(self.variableDatumRecords))
        for anObj in self.fixedDatumRecords:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DataQueryReliablePdu, self).parse(input_stream)
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.requestID = input_stream.read_unsigned_int()
        self.timeInterval = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumRecords.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumRecords.append(element)


class MinefieldStatePdu(MinefieldFamilyPdu):
    """information about the complete minefield. The minefield presence, perimiter, etc. Section 7.9.2 COMPLETE"""

    def __init__(self):
        """ Initializer for MinefieldStatePdu"""
        super(MinefieldStatePdu, self).__init__()
        self.minefieldID = MinefieldIdentifier()
        """ Minefield ID"""
        self.minefieldSequence = 0
        """ Minefield sequence"""
        self.forceID = 0
        """ force ID"""
        self.numberOfPerimeterPoints = 0
        """ Number of permieter points"""
        self.minefieldType = EntityType()
        """ type of minefield"""
        self.numberOfMineTypes = 0
        """ how many mine types"""
        self.minefieldLocation = Vector3Double()
        """ location of center of minefield in world coords"""
        self.minefieldOrientation = EulerAngles()
        """ orientation of minefield"""
        self.appearance = 0
        """ appearance bitflags"""
        self.protocolMode = 0
        """ protocolMode. First two bits are the protocol mode, 14 bits reserved."""
        self.perimeterPoints = []
        """ perimeter points for the minefield"""
        self.mineType = []
        """ Type of mines"""
        self.pduType = 37
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(MinefieldStatePdu, self).serialize(output_stream)
        self.minefieldID.serialize(output_stream)
        output_stream.write_unsigned_short(self.minefieldSequence)
        output_stream.write_unsigned_byte(self.forceID)
        output_stream.write_unsigned_byte(len(self.perimeterPoints))
        self.minefieldType.serialize(output_stream)
        output_stream.write_unsigned_short(len(self.mineType))
        self.minefieldLocation.serialize(output_stream)
        self.minefieldOrientation.serialize(output_stream)
        output_stream.write_unsigned_short(self.appearance)
        output_stream.write_unsigned_short(self.protocolMode)
        for anObj in self.perimeterPoints:
            anObj.serialize(output_stream)

        for anObj in self.mineType:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(MinefieldStatePdu, self).parse(input_stream)
        self.minefieldID.parse(input_stream)
        self.minefieldSequence = input_stream.read_unsigned_short()
        self.forceID = input_stream.read_unsigned_byte()
        self.numberOfPerimeterPoints = input_stream.read_unsigned_byte()
        self.minefieldType.parse(input_stream)
        self.numberOfMineTypes = input_stream.read_unsigned_short()
        self.minefieldLocation.parse(input_stream)
        self.minefieldOrientation.parse(input_stream)
        self.appearance = input_stream.read_unsigned_short()
        self.protocolMode = input_stream.read_unsigned_short()
        for idx in range(0, self.numberOfPerimeterPoints):
            element = null()
            element.parse(input_stream)
            self.perimeterPoints.append(element)

        for idx in range(0, self.numberOfMineTypes):
            element = null()
            element.parse(input_stream)
            self.mineType.append(element)


class DataReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.10: issued in response to a data query R or set dataR pdu. Needs manual intervention      to fix padding on variable datums. UNFINSIHED"""

    def __init__(self):
        """ Initializer for DataReliablePdu"""
        super(DataReliablePdu, self).__init__()
        self.requestID = 0
        """ Request ID"""
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding"""
        self.pad2 = 0
        """ padding"""
        self.numberOfFixedDatumRecords = 0
        """ Fixed datum record count"""
        self.numberOfVariableDatumRecords = 0
        """ variable datum record count"""
        self.fixedDatumRecords = []
        """ Fixed datum records"""
        self.variableDatumRecords = []
        """ Variable datum records"""
        self.pduType = 60
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DataReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_int(len(self.fixedDatumRecords))
        output_stream.write_unsigned_int(len(self.variableDatumRecords))
        for anObj in self.fixedDatumRecords:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DataReliablePdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumRecords.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumRecords.append(element)


class CommentPdu(SimulationManagementFamilyPdu):
    """ Arbitrary messages can be entered into the data stream via use of this PDU. Section 7.5.13 COMPLETE"""

    def __init__(self):
        """ Initializer for CommentPdu"""
        super(CommentPdu, self).__init__()
        self.numberOfFixedDatumRecords = 0
        """ Number of fixed datum records"""
        self.numberOfVariableDatumRecords = 0
        """ Number of variable datum records"""
        self.fixedDatums = []
        """ variable length list of fixed datums"""
        self.variableDatums = []
        """ variable length list of variable length datums"""
        self.pduType = 22
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(CommentPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(len(self.fixedDatums))
        output_stream.write_unsigned_int(len(self.variableDatums))
        for anObj in self.fixedDatums:
            anObj.serialize(output_stream)

        for anObj in self.variableDatums:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(CommentPdu, self).parse(input_stream)
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatums.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatums.append(element)


class CommentReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.12: Arbitrary messages. Only reliable this time. Neds manual intervention     to fix padding in variable datums. UNFINISHED"""

    def __init__(self):
        """ Initializer for CommentReliablePdu"""
        super(CommentReliablePdu, self).__init__()
        self.numberOfFixedDatumRecords = 0
        """ Fixed datum record count"""
        self.numberOfVariableDatumRecords = 0
        """ variable datum record count"""
        self.fixedDatumRecords = []
        """ Fixed datum records"""
        self.variableDatumRecords = []
        """ Variable datum records"""
        self.pduType = 62
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(CommentReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(len(self.fixedDatumRecords))
        output_stream.write_unsigned_int(len(self.variableDatumRecords))
        for anObj in self.fixedDatumRecords:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(CommentReliablePdu, self).parse(input_stream)
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumRecords.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumRecords.append(element)


class DirectedEnergyFirePdu(WarfareFamilyPdu):
    """Firing of a directed energy weapon shall be communicated by issuing a Directed Energy Fire PDU Section 7.3.4  COMPLETE"""

    def __init__(self):
        """ Initializer for DirectedEnergyFirePdu"""
        super(DirectedEnergyFirePdu, self).__init__()
        self.munitionType = EntityType()
        """ Field shall identify the munition type enumeration for the DE weapon beam, Section 7.3.4 """
        self.shotStartTime = ClockTime()
        """ Field shall indicate the simulation time at start of the shot, Section 7.3.4 """
        self.commulativeShotTime = 0
        """ Field shall indicate the current cumulative duration of the shot, Section 7.3.4 """
        self.ApertureEmitterLocation = Vector3Float()
        """ Field shall identify the location of the DE weapon aperture/emitter, Section 7.3.4 """
        self.apertureDiameter = 0
        """ Field shall identify the beam diameter at the aperture/emitter, Section 7.3.4 """
        self.wavelength = 0
        """ Field shall identify the emissions wavelength in units of meters, Section 7.3.4 """
        self.peakIrradiance = 0
        """ Field shall identify the current peak irradiance of emissions in units of Watts per square meter, Section 7.3.4 """
        self.pulseRepetitionFrequency = 0
        """ field shall identify the current pulse repetition frequency in units of cycles per second (Hertz), Section 7.3.4 """
        self.pulseWidth = 0
        """ field shall identify the pulse width emissions in units of seconds, Section 7.3.4"""
        self.flags = 0
        """ 16bit Boolean field shall contain various flags to indicate status information needed to process a DE, Section 7.3.4 """
        self.pulseShape = 0
        """ Field shall identify the pulse shape and shall be represented as an 8-bit enumeration, Section 7.3.4 """
        self.padding1 = 0
        """ padding, Section 7.3.4 """
        self.padding2 = 0
        """ padding, Section 7.3.4 """
        self.padding3 = 0
        """ padding, Section 7.3.4 """
        self.numberOfDERecords = 0
        """ Field shall specify the number of DE records, Section 7.3.4 """
        self.dERecords = []
        """ Fields shall contain one or more DE records, records shall conform to the variable record format (Section6.2.82), Section 7.3.4"""
        self.pduType = 68
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DirectedEnergyFirePdu, self).serialize(output_stream)
        self.munitionType.serialize(output_stream)
        self.shotStartTime.serialize(output_stream)
        output_stream.write_float(self.commulativeShotTime)
        self.ApertureEmitterLocation.serialize(output_stream)
        output_stream.write_float(self.apertureDiameter)
        output_stream.write_float(self.wavelength)
        output_stream.write_float(self.peakIrradiance)
        output_stream.write_float(self.pulseRepetitionFrequency)
        output_stream.write_int(self.pulseWidth)
        output_stream.write_int(self.flags)
        output_stream.write_byte(self.pulseShape)
        output_stream.write_unsigned_byte(self.padding1)
        output_stream.write_unsigned_int(self.padding2)
        output_stream.write_unsigned_short(self.padding3)
        output_stream.write_unsigned_short(len(self.dERecords))
        for anObj in self.dERecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DirectedEnergyFirePdu, self).parse(input_stream)
        self.munitionType.parse(input_stream)
        self.shotStartTime.parse(input_stream)
        self.commulativeShotTime = input_stream.read_float()
        self.ApertureEmitterLocation.parse(input_stream)
        self.apertureDiameter = input_stream.read_float()
        self.wavelength = input_stream.read_float()
        self.peakIrradiance = input_stream.read_float()
        self.pulseRepetitionFrequency = input_stream.read_float()
        self.pulseWidth = input_stream.read_int()
        self.flags = input_stream.read_int()
        self.pulseShape = input_stream.read_byte()
        self.padding1 = input_stream.read_unsigned_byte()
        self.padding2 = input_stream.read_unsigned_int()
        self.padding3 = input_stream.read_unsigned_short()
        self.numberOfDERecords = input_stream.read_unsigned_short()
        for idx in range(0, self.numberOfDERecords):
            element = null()
            element.parse(input_stream)
            self.dERecords.append(element)


class DetonationPdu(WarfareFamilyPdu):
    """Detonation or impact of munitions, as well as, non-munition explosions, the burst or initial bloom of chaff, and the ignition of a flare shall be indicated. Section 7.3.3  COMPLETE"""

    def __init__(self):
        """ Initializer for DetonationPdu"""
        super(DetonationPdu, self).__init__()
        self.explodingEntityID = EntityID()
        """ ID of the expendable entity, Section 7.3.3 """
        self.eventID = EventIdentifier()
        """ ID of event, Section 7.3.3"""
        self.velocity = Vector3Float()
        """ velocity of the munition immediately before detonation/impact, Section 7.3.3 """
        self.locationInWorldCoordinates = Vector3Double()
        """ location of the munition detonation, the expendable detonation, Section 7.3.3 """
        self.descriptor = MunitionDescriptor()
        """ Describes the detonation represented, Section 7.3.3 """
        self.locationOfEntityCoordinates = Vector3Float()
        """ Velocity of the ammunition, Section 7.3.3 """
        self.detonationResult = 0
        """ result of the detonation, Section 7.3.3 """
        self.numberOfVariableParameters = 0
        """ How many articulation parameters we have, Section 7.3.3 """
        self.pad = 0
        """ padding"""
        self.variableParameters = []
        """ specify the parameter values for each Variable Parameter record, Section 7.3.3 """
        self.pduType = 3
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(DetonationPdu, self).serialize(output_stream)
        self.explodingEntityID.serialize(output_stream)
        self.eventID.serialize(output_stream)
        self.velocity.serialize(output_stream)
        self.locationInWorldCoordinates.serialize(output_stream)
        self.descriptor.serialize(output_stream)
        self.locationOfEntityCoordinates.serialize(output_stream)
        output_stream.write_unsigned_byte(self.detonationResult)
        output_stream.write_unsigned_byte(len(self.variableParameters))
        output_stream.write_unsigned_short(self.pad)
        for anObj in self.variableParameters:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(DetonationPdu, self).parse(input_stream)
        self.explodingEntityID.parse(input_stream)
        self.eventID.parse(input_stream)
        self.velocity.parse(input_stream)
        self.locationInWorldCoordinates.parse(input_stream)
        self.descriptor.parse(input_stream)
        self.locationOfEntityCoordinates.parse(input_stream)
        self.detonationResult = input_stream.read_unsigned_byte()
        self.numberOfVariableParameters = input_stream.read_unsigned_byte()
        self.pad = input_stream.read_unsigned_short()
        for idx in range(0, self.numberOfVariableParameters):
            element = VariableParameter()
            element.parse(input_stream)
            self.variableParameters.append(element)


class SetDataPdu(SimulationManagementFamilyPdu):
    """Section 7.5.10. Change state information with the data contained in this. COMPLETE"""

    def __init__(self):
        """ Initializer for SetDataPdu"""
        super(SetDataPdu, self).__init__()
        self.requestID = 0
        """ ID of request"""
        self.padding1 = 0
        """ padding"""
        self.numberOfFixedDatumRecords = 0
        """ Number of fixed datum records"""
        self.numberOfVariableDatumRecords = 0
        """ Number of variable datum records"""
        self.fixedDatums = []
        """ variable length list of fixed datums"""
        self.variableDatums = []
        """ variable length list of variable length datums"""
        self.pduType = 19
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(SetDataPdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.padding1)
        output_stream.write_unsigned_int(len(self.fixedDatums))
        output_stream.write_unsigned_int(len(self.variableDatums))
        for anObj in self.fixedDatums:
            anObj.serialize(output_stream)

        for anObj in self.variableDatums:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(SetDataPdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.padding1 = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatums.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatums.append(element)


class RecordQueryReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.13: A request for one or more records of data from an entity. COMPLETE"""

    def __init__(self):
        """ Initializer for RecordQueryReliablePdu"""
        super(RecordQueryReliablePdu, self).__init__()
        self.requestID = 0
        """ request ID"""
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding. The spec is unclear and contradictory here."""
        self.pad2 = 0
        """ padding"""
        self.eventType = 0
        """ event type"""
        self.time = 0
        """ time"""
        self.numberOfRecords = 0
        """ numberOfRecords"""
        self.recordIDs = []
        """ record IDs"""
        self.pduType = 63
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(RecordQueryReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_short(self.eventType)
        output_stream.write_unsigned_int(self.time)
        output_stream.write_unsigned_int(len(self.recordIDs))
        for anObj in self.recordIDs:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(RecordQueryReliablePdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.eventType = input_stream.read_unsigned_short()
        self.time = input_stream.read_unsigned_int()
        self.numberOfRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfRecords):
            element = null()
            element.parse(input_stream)
            self.recordIDs.append(element)


class ActionResponsePdu(SimulationManagementFamilyPdu):
    """Section 7.5.8. response to an action request PDU. COMPLETE"""

    def __init__(self):
        """ Initializer for ActionResponsePdu"""
        super(ActionResponsePdu, self).__init__()
        self.requestID = 0
        """ Request ID that is unique"""
        self.requestStatus = 0
        """ Status of response"""
        self.numberOfFixedDatumRecords = 0
        """ Number of fixed datum records"""
        self.numberOfVariableDatumRecords = 0
        """ Number of variable datum records"""
        self.fixedDatums = []
        """ variable length list of fixed datums"""
        self.variableDatums = []
        """ variable length list of variable length datums"""
        self.pduType = 17
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ActionResponsePdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.requestStatus)
        output_stream.write_unsigned_int(len(self.fixedDatums))
        output_stream.write_unsigned_int(len(self.variableDatums))
        for anObj in self.fixedDatums:
            anObj.serialize(output_stream)

        for anObj in self.variableDatums:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ActionResponsePdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.requestStatus = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatums.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatums.append(element)


class EntityDamageStatusPdu(WarfareFamilyPdu):
    """shall be used to communicate detailed damage information sustained by an entity regardless of the source of the damage Section 7.3.5  COMPLETE"""

    def __init__(self):
        """ Initializer for EntityDamageStatusPdu"""
        super(EntityDamageStatusPdu, self).__init__()
        self.damagedEntityID = EntityID()
        """ Field shall identify the damaged entity (see 6.2.28), Section 7.3.4 COMPLETE"""
        self.padding1 = 0
        """ Padding."""
        self.padding2 = 0
        """ Padding."""
        self.numberOfDamageDescription = 0
        """ field shall specify the number of Damage Description records, Section 7.3.5"""
        self.damageDescriptionRecords = []
        """ Fields shall contain one or more Damage Description records (see 6.2.17) and may contain other Standard Variable records, Section 7.3.5"""
        self.pduType = 69
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(EntityDamageStatusPdu, self).serialize(output_stream)
        self.damagedEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.padding1)
        output_stream.write_unsigned_short(self.padding2)
        output_stream.write_unsigned_short(len(self.damageDescriptionRecords))
        for anObj in self.damageDescriptionRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(EntityDamageStatusPdu, self).parse(input_stream)
        self.damagedEntityID.parse(input_stream)
        self.padding1 = input_stream.read_unsigned_short()
        self.padding2 = input_stream.read_unsigned_short()
        self.numberOfDamageDescription = input_stream.read_unsigned_short()
        for idx in range(0, self.numberOfDamageDescription):
            element = null()
            element.parse(input_stream)
            self.damageDescriptionRecords.append(element)


class FirePdu(WarfareFamilyPdu):
    """ The firing of a weapon or expendable shall be communicated by issuing a Fire PDU. Sectioin 7.3.2. COMPLETE"""

    def __init__(self):
        """ Initializer for FirePdu"""
        super(FirePdu, self).__init__()
        self.munitionExpendibleID = EntityID()
        """ This field shall specify the entity identification of the fired munition or expendable. This field shall be represented by an Entity Identifier record (see 6.2.28)."""
        self.eventID = EventIdentifier()
        """ This field shall contain an identification generated by the firing entity to associate related firing and detonation events. This field shall be represented by an Event Identifier record (see 6.2.34)."""
        self.fireMissionIndex = 0
        """ This field shall identify the fire mission (see 5.4.3.3). This field shall be representedby a 32-bit unsigned integer."""
        self.locationInWorldCoordinates = Vector3Double()
        """ This field shall specify the location, in world coordinates, from which the munition was launched, and shall be represented by a World Coordinates record (see 6.2.97)."""
        self.descriptor = MunitionDescriptor()
        """ This field shall describe the firing or launch of a munition or expendable represented by one of the following types of Descriptor records: Munition Descriptor (6.2.20.2) or Expendable Descriptor (6.2.20.4)."""
        self.velocity = Vector3Float()
        """ This field shall specify the velocity of the fired munition at the point when the issuing simulation application intends the externally visible effects of the launch (e.g. exhaust plume or muzzle blast) to first become apparent. The velocity shall be represented in world coordinates. This field shall be represented by a Linear Velocity Vector record [see 6.2.95 item c)]."""
        self.range = 0
        """ This field shall specify the range that an entitys fire control system has assumed in computing the fire control solution. This field shall be represented by a 32-bit floating point number in meters. For systems where range is unknown or unavailable, this field shall contain a value of zero."""
        self.pduType = 2
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(FirePdu, self).serialize(output_stream)
        self.munitionExpendibleID.serialize(output_stream)
        self.eventID.serialize(output_stream)
        output_stream.write_unsigned_int(self.fireMissionIndex)
        self.locationInWorldCoordinates.serialize(output_stream)
        self.descriptor.serialize(output_stream)
        self.velocity.serialize(output_stream)
        output_stream.write_float(self.range)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(FirePdu, self).parse(input_stream)
        self.munitionExpendibleID.parse(input_stream)
        self.eventID.parse(input_stream)
        self.fireMissionIndex = input_stream.read_unsigned_int()
        self.locationInWorldCoordinates.parse(input_stream)
        self.descriptor.parse(input_stream)
        self.velocity.parse(input_stream)
        self.range = input_stream.read_float()


class ReceiverPdu(RadioCommunicationsFamilyPdu):
    """ Communication of a receiver state. Section 7.7.4 COMPLETE"""

    def __init__(self):
        """ Initializer for ReceiverPdu"""
        super(ReceiverPdu, self).__init__()
        self.receiverState = 0
        """ encoding scheme used, and enumeration"""
        self.padding1 = 0
        """ padding"""
        self.receivedPoser = 0
        """ received power"""
        self.transmitterEntityId = EntityID()
        """ ID of transmitter"""
        self.transmitterRadioId = 0
        """ ID of transmitting radio"""
        self.pduType = 27
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ReceiverPdu, self).serialize(output_stream)
        output_stream.write_unsigned_short(self.receiverState)
        output_stream.write_unsigned_short(self.padding1)
        output_stream.write_float(self.receivedPoser)
        self.transmitterEntityId.serialize(output_stream)
        output_stream.write_unsigned_short(self.transmitterRadioId)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ReceiverPdu, self).parse(input_stream)
        self.receiverState = input_stream.read_unsigned_short()
        self.padding1 = input_stream.read_unsigned_short()
        self.receivedPoser = input_stream.read_float()
        self.transmitterEntityId.parse(input_stream)
        self.transmitterRadioId = input_stream.read_unsigned_short()


class UaPdu(DistributedEmissionsFamilyPdu):
    """ Information about underwater acoustic emmissions. This requires manual cleanup.  The beam data records should ALL be a the finish, rather than attached to each emitter system. Section 7.6.4. UNFINISHED"""

    def __init__(self):
        """ Initializer for UaPdu"""
        super(UaPdu, self).__init__()
        self.emittingEntityID = EntityID()
        """ ID of the entity that is the source of the emission"""
        self.eventID = EventIdentifier()
        """ ID of event"""
        self.stateChangeIndicator = 0
        """ This field shall be used to indicate whether the data in the UA PDU represent a state update or data that have changed since issuance of the last UA PDU"""
        self.pad = 0
        """ padding"""
        self.passiveParameterIndex = 0
        """ This field indicates which database record (or file) shall be used in the definition of passive signature (unintentional) emissions of the entity. The indicated database record (or  file) shall define all noise generated as a function of propulsion plant configurations and associated  auxiliaries."""
        self.propulsionPlantConfiguration = 0
        """ This field shall specify the entity propulsion plant configuration. This field is used to determine the passive signature characteristics of an entity."""
        self.numberOfShafts = 0
        """  This field shall represent the number of shafts on a platform"""
        self.numberOfAPAs = 0
        """ This field shall indicate the number of APAs described in the current UA PDU"""
        self.numberOfUAEmitterSystems = 0
        """ This field shall specify the number of UA emitter systems being described in the current UA PDU"""
        self.shaftRPMs = []
        """ shaft RPM values. THIS IS WRONG. It has the wrong class in the list."""
        self.apaData = []
        """ apaData. THIS IS WRONG. It has the worng class in the list."""
        self.emitterSystems = []
        """ THIS IS WRONG. It has the wrong class in the list."""
        self.pduType = 29
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(UaPdu, self).serialize(output_stream)
        self.emittingEntityID.serialize(output_stream)
        self.eventID.serialize(output_stream)
        output_stream.write_byte(self.stateChangeIndicator)
        output_stream.write_byte(self.pad)
        output_stream.write_unsigned_short(self.passiveParameterIndex)
        output_stream.write_unsigned_byte(self.propulsionPlantConfiguration)
        output_stream.write_unsigned_byte(len(self.shaftRPMs))
        output_stream.write_unsigned_byte(len(self.apaData))
        output_stream.write_unsigned_byte(len(self.emitterSystems))
        for anObj in self.shaftRPMs:
            anObj.serialize(output_stream)

        for anObj in self.apaData:
            anObj.serialize(output_stream)

        for anObj in self.emitterSystems:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(UaPdu, self).parse(input_stream)
        self.emittingEntityID.parse(input_stream)
        self.eventID.parse(input_stream)
        self.stateChangeIndicator = input_stream.read_byte()
        self.pad = input_stream.read_byte()
        self.passiveParameterIndex = input_stream.read_unsigned_short()
        self.propulsionPlantConfiguration = input_stream.read_unsigned_byte()
        self.numberOfShafts = input_stream.read_unsigned_byte()
        self.numberOfAPAs = input_stream.read_unsigned_byte()
        self.numberOfUAEmitterSystems = input_stream.read_unsigned_byte()
        for idx in range(0, self.numberOfShafts):
            element = VariableParameter()
            element.parse(input_stream)
            self.shaftRPMs.append(element)

        for idx in range(0, self.numberOfAPAs):
            element = VariableParameter()
            element.parse(input_stream)
            self.apaData.append(element)

        for idx in range(0, self.numberOfUAEmitterSystems):
            element = VariableParameter()
            element.parse(input_stream)
            self.emitterSystems.append(element)


class IntercomControlPdu(RadioCommunicationsFamilyPdu):
    """ Detailed inofrmation about the state of an intercom device and the actions it is requestion         of another intercom device, or the response to a requested action. Required manual intervention to fix the intercom parameters,        which can be of varialbe length. Section 7.7.5 UNFINSISHED"""

    def __init__(self):
        """ Initializer for IntercomControlPdu"""
        super(IntercomControlPdu, self).__init__()
        self.controlType = 0
        """ control type"""
        self.communicationsChannelType = 0
        """ control type"""
        self.sourceEntityID = EntityID()
        """ Source entity ID"""
        self.sourceCommunicationsDeviceID = 0
        """ The specific intercom device being simulated within an entity."""
        self.sourceLineID = 0
        """ Line number to which the intercom control refers"""
        self.transmitPriority = 0
        """ priority of this message relative to transmissons from other intercom devices"""
        self.transmitLineState = 0
        """ current transmit state of the line"""
        self.command = 0
        """ detailed type requested."""
        self.masterEntityID = EntityID()
        """ eid of the entity that has created this intercom channel."""
        self.masterCommunicationsDeviceID = 0
        """ specific intercom device that has created this intercom channel"""
        self.intercomParametersLength = 0
        """ number of intercom parameters"""
        self.intercomParameters = []
        """ ^^^This is wrong the length of the data field is variable. Using a long for now."""
        self.pduType = 32
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(IntercomControlPdu, self).serialize(output_stream)
        output_stream.write_unsigned_byte(self.controlType)
        output_stream.write_unsigned_byte(self.communicationsChannelType)
        self.sourceEntityID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.sourceCommunicationsDeviceID)
        output_stream.write_unsigned_byte(self.sourceLineID)
        output_stream.write_unsigned_byte(self.transmitPriority)
        output_stream.write_unsigned_byte(self.transmitLineState)
        output_stream.write_unsigned_byte(self.command)
        self.masterEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.masterCommunicationsDeviceID)
        output_stream.write_unsigned_int(len(self.intercomParameters))
        for anObj in self.intercomParameters:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(IntercomControlPdu, self).parse(input_stream)
        self.controlType = input_stream.read_unsigned_byte()
        self.communicationsChannelType = input_stream.read_unsigned_byte()
        self.sourceEntityID.parse(input_stream)
        self.sourceCommunicationsDeviceID = input_stream.read_unsigned_byte()
        self.sourceLineID = input_stream.read_unsigned_byte()
        self.transmitPriority = input_stream.read_unsigned_byte()
        self.transmitLineState = input_stream.read_unsigned_byte()
        self.command = input_stream.read_unsigned_byte()
        self.masterEntityID.parse(input_stream)
        self.masterCommunicationsDeviceID = input_stream.read_unsigned_short()
        self.intercomParametersLength = input_stream.read_unsigned_int()
        for idx in range(0, self.intercomParametersLength):
            element = VariableParameter()
            element.parse(input_stream)
            self.intercomParameters.append(element)


class SignalPdu(RadioCommunicationsFamilyPdu):
    """ Detailed information about a radio transmitter. This PDU requires manually written code to complete. The encodingScheme field can be used in multiple        ways, which requires hand-written code to finish. Section 7.7.3. UNFINISHED"""

    def __init__(self):
        """ Initializer for SignalPdu"""
        super(SignalPdu, self).__init__()

        self.entityID = EntityID()

        self.radioID = 0

        self.encodingScheme = 0
        """ encoding scheme used, and enumeration"""
        self.tdlType = 0
        """ tdl type"""
        self.sampleRate = 0
        """ sample rate"""
        self.dataLength = 0
        """ length od data"""
        self.samples = 0
        """ number of samples"""
        self.data = []
        """ list of eight bit values"""
        self.pduType = 26
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(SignalPdu, self).serialize(output_stream)
        self.entityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.radioID)
        output_stream.write_unsigned_short(self.encodingScheme)
        output_stream.write_unsigned_short(self.tdlType)
        output_stream.write_unsigned_int(self.sampleRate)
        output_stream.write_short(len(self.data) * 8)
        output_stream.write_short(self.samples)
        for b in self.data:
            output_stream.write_byte(b)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(SignalPdu, self).parse(input_stream)
        self.entityID.parse(input_stream)
        self.radioID = input_stream.read_unsigned_short()
        self.encodingScheme = input_stream.read_unsigned_short()
        self.tdlType = input_stream.read_unsigned_short()
        self.sampleRate = input_stream.read_unsigned_int()
        self.dataLength = input_stream.read_short()
        self.samples = input_stream.read_short()
        for idx in range(0, self.dataLength // 8):
            element = input_stream.read_byte()
            self.data.append(element)


class RemoveEntityReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.2: Removal of an entity , reliable. COMPLETE"""

    def __init__(self):
        """ Initializer for RemoveEntityReliablePdu"""
        super(RemoveEntityReliablePdu, self).__init__()
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding"""
        self.pad2 = 0
        """ padding"""
        self.requestID = 0
        """ Request ID"""
        self.pduType = 52
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(RemoveEntityReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(RemoveEntityReliablePdu, self).parse(input_stream)
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.requestID = input_stream.read_unsigned_int()


class SeesPdu(DistributedEmissionsFamilyPdu):
    """ SEES PDU, supplemental emissions entity state information. Section 7.6.6 COMPLETE"""

    def __init__(self):
        """ Initializer for SeesPdu"""
        super(SeesPdu, self).__init__()
        self.orginatingEntityID = EntityID()
        """ Originating entity ID"""
        self.infraredSignatureRepresentationIndex = 0
        """ IR Signature representation index"""
        self.acousticSignatureRepresentationIndex = 0
        """ acoustic Signature representation index"""
        self.radarCrossSectionSignatureRepresentationIndex = 0
        """ radar cross section representation index"""
        self.numberOfPropulsionSystems = 0
        """ how many propulsion systems"""
        self.numberOfVectoringNozzleSystems = 0
        """ how many vectoring nozzle systems"""
        self.propulsionSystemData = []
        """ variable length list of propulsion system data"""
        self.vectoringSystemData = []
        """ variable length list of vectoring system data"""
        self.pduType = 30
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(SeesPdu, self).serialize(output_stream)
        self.orginatingEntityID.serialize(output_stream)
        output_stream.write_unsigned_short(self.infraredSignatureRepresentationIndex)
        output_stream.write_unsigned_short(self.acousticSignatureRepresentationIndex)
        output_stream.write_unsigned_short(self.radarCrossSectionSignatureRepresentationIndex)
        output_stream.write_unsigned_short(len(self.propulsionSystemData))
        output_stream.write_unsigned_short(len(self.vectoringSystemData))
        for anObj in self.propulsionSystemData:
            anObj.serialize(output_stream)

        for anObj in self.vectoringSystemData:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(SeesPdu, self).parse(input_stream)
        self.orginatingEntityID.parse(input_stream)
        self.infraredSignatureRepresentationIndex = input_stream.read_unsigned_short()
        self.acousticSignatureRepresentationIndex = input_stream.read_unsigned_short()
        self.radarCrossSectionSignatureRepresentationIndex = input_stream.read_unsigned_short()
        self.numberOfPropulsionSystems = input_stream.read_unsigned_short()
        self.numberOfVectoringNozzleSystems = input_stream.read_unsigned_short()
        for idx in range(0, self.numberOfPropulsionSystems):
            element = null()
            element.parse(input_stream)
            self.propulsionSystemData.append(element)

        for idx in range(0, self.numberOfVectoringNozzleSystems):
            element = null()
            element.parse(input_stream)
            self.vectoringSystemData.append(element)


class CreateEntityReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.1: creation of an entity , reliable. COMPLETE"""

    def __init__(self):
        """ Initializer for CreateEntityReliablePdu"""
        super(CreateEntityReliablePdu, self).__init__()
        self.requiredReliabilityService = 0
        """ level of reliability service used for this transaction"""
        self.pad1 = 0
        """ padding"""
        self.pad2 = 0
        """ padding"""
        self.requestID = 0
        """ Request ID"""
        self.pduType = 51
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(CreateEntityReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_byte(self.requiredReliabilityService)
        output_stream.write_unsigned_short(self.pad1)
        output_stream.write_unsigned_byte(self.pad2)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(CreateEntityReliablePdu, self).parse(input_stream)
        self.requiredReliabilityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_short()
        self.pad2 = input_stream.read_unsigned_byte()
        self.requestID = input_stream.read_unsigned_int()


class StopFreezeReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.4: Stop freeze simulation, relaible. COMPLETE"""

    def __init__(self):
        """ Initializer for StopFreezeReliablePdu"""
        super(StopFreezeReliablePdu, self).__init__()
        self.realWorldTime = ClockTime()
        """ time in real world for this operation to happen"""
        self.reason = 0
        """ Reason for stopping/freezing simulation"""
        self.frozenBehavior = 0
        """ internal behvior of the simulation while frozen"""
        self.requiredReliablityService = 0
        """ reliablity level"""
        self.pad1 = 0
        """ padding"""
        self.requestID = 0
        """ Request ID"""
        self.pduType = 54
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(StopFreezeReliablePdu, self).serialize(output_stream)
        self.realWorldTime.serialize(output_stream)
        output_stream.write_unsigned_byte(self.reason)
        output_stream.write_unsigned_byte(self.frozenBehavior)
        output_stream.write_unsigned_byte(self.requiredReliablityService)
        output_stream.write_unsigned_byte(self.pad1)
        output_stream.write_unsigned_int(self.requestID)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(StopFreezeReliablePdu, self).parse(input_stream)
        self.realWorldTime.parse(input_stream)
        self.reason = input_stream.read_unsigned_byte()
        self.frozenBehavior = input_stream.read_unsigned_byte()
        self.requiredReliablityService = input_stream.read_unsigned_byte()
        self.pad1 = input_stream.read_unsigned_byte()
        self.requestID = input_stream.read_unsigned_int()


class EventReportReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.11: reports the occurance of a significatnt event to the simulation manager. Needs manual     intervention to fix padding in variable datums. UNFINISHED."""

    def __init__(self):
        """ Initializer for EventReportReliablePdu"""
        super(EventReportReliablePdu, self).__init__()
        self.eventType = 0
        """ Event type"""
        self.pad1 = 0
        """ padding"""
        self.numberOfFixedDatumRecords = 0
        """ Fixed datum record count"""
        self.numberOfVariableDatumRecords = 0
        """ variable datum record count"""
        self.fixedDatumRecords = []
        """ Fixed datum records"""
        self.variableDatumRecords = []
        """ Variable datum records"""
        self.pduType = 61
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(EventReportReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_short(self.eventType)
        output_stream.write_unsigned_int(self.pad1)
        output_stream.write_unsigned_int(len(self.fixedDatumRecords))
        output_stream.write_unsigned_int(len(self.variableDatumRecords))
        for anObj in self.fixedDatumRecords:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(EventReportReliablePdu, self).parse(input_stream)
        self.eventType = input_stream.read_unsigned_short()
        self.pad1 = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumRecords.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumRecords.append(element)


class MinefieldResponseNackPdu(MinefieldFamilyPdu):
    """proivde the means to request a retransmit of a minefield data pdu. Section 7.9.5 COMPLETE"""

    def __init__(self):
        """ Initializer for MinefieldResponseNackPdu"""
        super(MinefieldResponseNackPdu, self).__init__()
        self.minefieldID = EntityID()
        """ Minefield ID"""
        self.requestingEntityID = EntityID()
        """ entity ID making the request"""
        self.requestID = 0
        """ request ID"""
        self.numberOfMissingPdus = 0
        """ how many pdus were missing"""
        self.missingPduSequenceNumbers = []
        """ PDU sequence numbers that were missing"""
        self.pduType = 40
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(MinefieldResponseNackPdu, self).serialize(output_stream)
        self.minefieldID.serialize(output_stream)
        self.requestingEntityID.serialize(output_stream)
        output_stream.write_unsigned_byte(self.requestID)
        output_stream.write_unsigned_byte(len(self.missingPduSequenceNumbers))
        for anObj in self.missingPduSequenceNumbers:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(MinefieldResponseNackPdu, self).parse(input_stream)
        self.minefieldID.parse(input_stream)
        self.requestingEntityID.parse(input_stream)
        self.requestID = input_stream.read_unsigned_byte()
        self.numberOfMissingPdus = input_stream.read_unsigned_byte()
        for idx in range(0, self.numberOfMissingPdus):
            element = null()
            element.parse(input_stream)
            self.missingPduSequenceNumbers.append(element)


class ActionResponseReliablePdu(SimulationManagementWithReliabilityFamilyPdu):
    """Section 5.3.12.7: Response from an entity to an action request PDU. COMPLETE"""

    def __init__(self):
        """ Initializer for ActionResponseReliablePdu"""
        super(ActionResponseReliablePdu, self).__init__()
        self.requestID = 0
        """ request ID"""
        self.responseStatus = 0
        """ status of response"""
        self.numberOfFixedDatumRecords = 0
        """ Fixed datum record count"""
        self.numberOfVariableDatumRecords = 0
        """ variable datum record count"""
        self.fixedDatumRecords = []
        """ Fixed datum records"""
        self.variableDatumRecords = []
        """ Variable datum records"""
        self.pduType = 57
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(ActionResponseReliablePdu, self).serialize(output_stream)
        output_stream.write_unsigned_int(self.requestID)
        output_stream.write_unsigned_int(self.responseStatus)
        output_stream.write_unsigned_int(len(self.fixedDatumRecords))
        output_stream.write_unsigned_int(len(self.variableDatumRecords))
        for anObj in self.fixedDatumRecords:
            anObj.serialize(output_stream)

        for anObj in self.variableDatumRecords:
            anObj.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(ActionResponseReliablePdu, self).parse(input_stream)
        self.requestID = input_stream.read_unsigned_int()
        self.responseStatus = input_stream.read_unsigned_int()
        self.numberOfFixedDatumRecords = input_stream.read_unsigned_int()
        self.numberOfVariableDatumRecords = input_stream.read_unsigned_int()
        for idx in range(0, self.numberOfFixedDatumRecords):
            element = FixedDatum()
            element.parse(input_stream)
            self.fixedDatumRecords.append(element)

        for idx in range(0, self.numberOfVariableDatumRecords):
            element = VariableDatum()
            element.parse(input_stream)
            self.variableDatumRecords.append(element)


class IsPartOfPdu(EntityManagementFamilyPdu):
    """ The joining of two or more simulation entities is communicated by this PDU. Section 7.8.5 COMPLETE"""

    def __init__(self):
        """ Initializer for IsPartOfPdu"""
        super(IsPartOfPdu, self).__init__()
        self.orginatingEntityID = EntityID()
        """ ID of entity originating PDU"""
        self.receivingEntityID = EntityID()
        """ ID of entity receiving PDU"""
        self.relationship = Relationship()
        """ relationship of joined parts"""
        self.partLocation = Vector3Float()
        """ location of part centroid of part in host's coordinate system. x=range, y=bearing, z=0"""
        self.namedLocationID = NamedLocationIdentification()
        """ named location"""
        self.partEntityType = EntityType()
        """ entity type"""
        self.pduType = 36
        """ initialize value """

    def serialize(self, output_stream):
        """serialize the class """
        super(IsPartOfPdu, self).serialize(output_stream)
        self.orginatingEntityID.serialize(output_stream)
        self.receivingEntityID.serialize(output_stream)
        self.relationship.serialize(output_stream)
        self.partLocation.serialize(output_stream)
        self.namedLocationID.serialize(output_stream)
        self.partEntityType.serialize(output_stream)

    def parse(self, input_stream):
        """"Parse a message. This may recursively call embedded objects."""

        super(IsPartOfPdu, self).parse(input_stream)
        self.orginatingEntityID.parse(input_stream)
        self.receivingEntityID.parse(input_stream)
        self.relationship.parse(input_stream)
        self.partLocation.parse(input_stream)
        self.namedLocationID.parse(input_stream)
        self.partEntityType.parse(input_stream)
