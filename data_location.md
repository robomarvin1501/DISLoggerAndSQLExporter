Recurring Details
===============
The below items recur a lot. This is the plan to infer them.  
Have a switch in the logger that decides whether or not to export.  
This can be cli args, but if not provided, then it should check when starting.
- LoggerFile
  - In logger: The supplied file name
  - In exporter: The supplied file name
- ExportTime
  - In logger: DISReceiver.starting_timestamp
  - In exporter: Create an ExportTime variable
- ExerciseId
  - pdu.exerciseID



EntityState
==============

####EntityAppearance
- This field contains the data concerning how it looks. It is received as a large base 10 integer
- When converted to binary, this binary number holds the data in a readable manner
- All fields hold diogits starting counting from the **LEAST** significant digit

###Ints  
- SenderId
  - entityID (site=site, host=application, entity=entity)
- IntType and IntValue
  - LifeformState
    - This appears to be a decimal interpretation of a hex value  
      of multiple 0x10000 starting at 0x10000, ending at 0x60000 
  - Damage
    - Bits 3-4 of EntityAppearance
  - Weapon1
    - ~~A decimal representation of the hex number in EntityStatePdu.dis.appearance~~
    - entityAppearance
  - ~~Weapon2~~
    - ~~Not always 0, seems to be coming from somewhere? Where though?~~
    - ~~Either 0 or 67108864 (0x4000000)~~
  - forceId
    - force_id
- WorldTime
  - WorldTime
- PacketTime
  - PacketTime
- LoggerFile
- ExportTime
- ExerciseId
###Locations
- SenderId
  - entityID (site=site, host=application, entity=entity)
- GeoLocation
  - entityLocation (x, y, z)
- GeoVelocity
  - entityLinearVelocity
- Psi, Theta, Phi
  - entityOrientation
- WorldTime
- PacketTime
- LoggerFile
- ExportTime
- ExerciseId

###Texts
- SenderId
  - entityID (site=site, host=application, entity=entity)
- TextType
  - Entity
  - MarkingText
  - EntityType
- TextValue
  - Entity: Do we need this? It's just Added/Removed
  - ''.join(map(chr, pdu.marking.characters))
  - entityType (or alternativeEntityType) in the following order
    - entityKind:domain:country:category:subcategory:specific:extra