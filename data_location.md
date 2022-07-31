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
  - frame.WorldTime (epoch seconds: use datetime.datetime.fromtimestamp)
- PacketTime
  - frame.PacketTime
- LoggerFile
- ExportTime
- ExerciseId
###Locations



###Texts