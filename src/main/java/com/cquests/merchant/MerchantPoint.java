package com.cquests.merchant;

import org.bukkit.*;

public record MerchantPoint(String world,double x,double y,double z,float yaw) {
    public static MerchantPoint at(Location l){return new MerchantPoint(l.getWorld().getName(),l.getX(),l.getY(),l.getZ(),l.getYaw());}
    public Location location(){World w=Bukkit.getWorld(world);return w==null?null:new Location(w,x,y,z,yaw,0);}
    public String encode(){return world+";"+x+";"+y+";"+z+";"+yaw;}
    public static MerchantPoint decode(String value){
        if(value==null)return null;String[] p=value.split(";");if(p.length!=5)return null;
        try{double x=Double.parseDouble(p[1]),y=Double.parseDouble(p[2]),z=Double.parseDouble(p[3]);float yaw=Float.parseFloat(p[4]);
            return Double.isFinite(x)&&Double.isFinite(y)&&Double.isFinite(z)&&Float.isFinite(yaw)?new MerchantPoint(p[0],x,y,z,yaw):null;
        }catch(NumberFormatException e){return null;}
    }
}
