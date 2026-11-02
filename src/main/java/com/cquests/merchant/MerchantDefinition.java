package com.cquests.merchant;

import java.util.*;

public record MerchantDefinition(String id,String name,String profession,MerchantPoint spawn,
                                 List<MerchantPoint> route,MerchantPoint shop,List<TradeOffer> offers,boolean enabled,long revision) {
    public MerchantDefinition{route=List.copyOf(route);offers=Collections.unmodifiableList(new ArrayList<>(offers));}
}
