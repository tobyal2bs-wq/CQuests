package com.cquests.listener;

import org.bukkit.NamespacedKey;
import org.bukkit.block.Block;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import java.util.BitSet;
import java.util.Objects;

/** Compact chunk-owned marks: no global tracking map, cap reset, or restart-based quest farming. */
final class PlacedBlocks {
    private static final NamespacedKey PLACED=Objects.requireNonNull(NamespacedKey.fromString("cquests:quest_placed_blocks"));
    private static final NamespacedKey COUNTED=Objects.requireNonNull(NamespacedKey.fromString("cquests:quest_counted_placements"));

    void add(Block block) { change(block,PLACED,true); }
    boolean firstPlacementAt(Block block) { return !change(block,COUNTED,true); }
    boolean remove(Block block) { return change(block,PLACED,false); }

    /** Called only by block events on the owning region. Chunk saving persists these marks normally. */
    private static boolean change(Block block,NamespacedKey key,boolean value) {
        PersistentDataContainer data=block.getChunk().getPersistentDataContainer();
        byte[] bytes=data.get(key,PersistentDataType.BYTE_ARRAY);
        if(bytes==null&&!value)return false;
        BitSet bits=bytes==null?new BitSet():BitSet.valueOf(bytes);
        int index=((block.getY()-block.getWorld().getMinHeight())<<8)|((block.getZ()&15)<<4)|(block.getX()&15);
        boolean previous=bits.get(index);
        if(previous!=value){
            bits.set(index,value);
            if(bits.isEmpty())data.remove(key);else data.set(key,PersistentDataType.BYTE_ARRAY,bits.toByteArray());
        }
        return previous;
    }
}
