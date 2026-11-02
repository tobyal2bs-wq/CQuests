package com.cquests.dialogue;

import java.util.*;

/** Bounded text wrapping keeps the lifted nameplate clear of long dialogue. */
public record SpeechTiming(int characterTicks,int readingTicks) {
    public SpeechTiming{characterTicks=Math.max(1,Math.min(10,characterTicks));readingTicks=Math.max(20,Math.min(400,readingTicks));}
    public static List<String> sentences(String plain){
        List<String> result=new ArrayList<>();
        for(String sentence:plain.split("(?<=[.!?])\\s+")){
            String rest=sentence.strip();while(rest.codePointCount(0,rest.length())>120){
                int limit=rest.offsetByCodePoints(0,120),cut=rest.lastIndexOf(' ',limit);if(cut<limit/2)cut=limit;
                result.add(rest.substring(0,cut));rest=rest.substring(cut).strip();
            }
            if(!rest.isBlank())result.add(rest);
        }
        return List.copyOf(result);
    }
}
