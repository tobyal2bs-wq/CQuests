package com.cquests.worldboss;


import org.joml.*;
import org.junit.jupiter.api.Test;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

class RigPolishTest {
    private Map<String,ModelRig.Model> models() throws Exception {
        try(var in=getClass().getResourceAsStream("/worldboss-models.json")) {
            return ModelRig.load(new InputStreamReader(in,StandardCharsets.UTF_8));
        }
    }
    @Test void everyPerformanceRemainsConnectedAndMatchesTheClient() throws Exception {
        for(var m:models().values()) {
            Set<String> names=new HashSet<>(m.attackAnimations());
            names.addAll(List.of("idle","walk","opening_"+m.id));
            for(String name:names) {
                var anim=m.anim(name);if(anim==null)continue;
                for(int sample=0;sample<=8;sample++) {
                    float time=anim.length()*sample/8;
                    var bones=ModelRig.pose(m,List.of(new ModelRig.Layer(anim,time,1)));
                    for(int i=0;i<m.bones.size();i++) {
                        var bone=m.bones.get(i);
                        if(bone.parent()<0 || !bone.name().startsWith("shin") && !bone.name().startsWith("fore") && !bone.name().startsWith("foot"))continue;
                        var channel=anim.bones().get(bone.name());
                        if(channel!=null && channel.pos()!=null)continue;
                        Vector3f expected=bones[bone.parent()].transformPosition(new Vector3f(bone.pivot()));
                        Vector3f actual=bones[i].transformPosition(new Vector3f(bone.pivot()));
                        assertTrue(expected.distance(actual)<.025f,m.id+" "+name+" detached "+bone.name()+" at "+time);
                    }
                    for(var cube:ModelRig.cubes(m,bones)) {
                        var t=Displays.transformation(cube);
                        var rendered=new Matrix4f().translation(t.getTranslation()).rotate(t.getLeftRotation()).scale(t.getScale()).rotate(t.getRightRotation());
                        for(int corner=0;corner<8;corner++) {
                            Vector3f a=cube.transformPosition(corner&1,corner>>1&1,corner>>2&1,new Vector3f());
                            Vector3f b=rendered.transformPosition(corner&1,corner>>1&1,corner>>2&1,new Vector3f());
                            assertTrue(a.isFinite() && a.distance(b)<.01,m.id+" "+name+" incorrect client transform at "+time);
                        }
                    }
                }
            }
        }
    }
    @Test void eachBossHasItsOwnOpeningWithoutDecorativeRings() throws Exception {
        Set<String> performances=new HashSet<>();
        for(var m:models().values()) {
            if(m.id.startsWith("decor_"))continue;
            var opening=m.anim("opening_"+m.id);
            assertNotNull(opening,m.id);assertFalse(opening.bones().isEmpty(),m.id);
            assertTrue(performances.add(opening.length()+":"+opening.bones().toString()),m.id+" duplicate performance");
            assertTrue(m.spawn.stream().noneMatch(s->s.num("ring",0)>0),m.id+" ring");
        }
    }
}

