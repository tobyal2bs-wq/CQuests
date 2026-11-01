package com.cquests.farm;

public record FarmArea(String id,String world,String region,int minY,int maxY,Polygon outline,boolean outside,int[] bounds) {
    public boolean candidate(String world,int x,int y,int z) {
        if(!this.world.equals(world)||y<minY||y>maxY||x<bounds[0]||x>bounds[3]||z<bounds[2]||z>bounds[5])return false;
        return outline.contains(x,z)!=outside;
    }
}
