EntityState
==============
###Ints  
- SenderId
  - entityID (site=site, host=application, entity=entity)
- IntType and IntValue
  - LifeformState
    - This appears to be a decimal interpretation of a hex value  
      of multiple 0x10000 starting at 0x10000, ending at 0x60000 
  - Damage
  - Weapon1
    - ~~A decimal representation of the hex number in EntityStatePdu.dis.appearance~~
    - entityAppearance
  - Weapon2
    - ~~Always 0?~~
    - Not always 0, seems to be coming from somewhere? Where though?
  - forceId
    - force_id
- WorldTime
  - frame.WorldTime (epoch seconds: use datetime.datetime.fromtimestamp)
- PacketTime
  - frame.PacketTime
- LoggerFile
- ExportTime
- ExerciseId
###Locations
###Texts