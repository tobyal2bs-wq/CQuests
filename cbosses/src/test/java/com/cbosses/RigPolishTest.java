package com.cbosses;

import com.cbosses.model.*;
import org.joml.*;
import org.junit.jupiter.api.Test;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

class RigPolishTest {
    @Test void restGeometryTouchesTheFloorAndBirdsHaveTwoEyes() throws Exception {
        for(var m:models().values()) {
            var cubes=ModelRig.cubes(m,ModelRig.pose(m,List.of(new ModelRig.Layer(m.anim("idle"),0,1))));
            float bottom=Float.POSITIVE_INFINITY;
            for(int i=0;i<cubes.length;i++) {
                var tag=m.cubes.get(i).tag();
                if(m.entranceOnly[i] || tag.startsWith("face:") && !tag.equals("face:idle"))continue;
                for(int k=0;k<8;k++)bottom=java.lang.Math.min(bottom,cubes[i].transformPosition(k&1,k>>1&1,k>>2&1,new Vector3f()).y);
            }
            assertEquals(0,bottom,.005,m.id+" must stand on the real posed floor");
            float sole=Float.POSITIVE_INFINITY;
            for(int i=0;i<cubes.length;i++) {
                int b=m.cubes.get(i).bone();boolean leg=false;
                while(b>=0){var bone=m.bones.get(b);leg|=bone.name().startsWith("leg")||bone.name().startsWith("foot");b=bone.parent();}
                if(leg)for(int k=0;k<8;k++)sole=java.lang.Math.min(sole,cubes[i].transformPosition(k&1,k>>1&1,k>>2&1,new Vector3f()).y);
            }
            if(Float.isFinite(sole))assertTrue(java.lang.Math.abs(sole)<.08,m.id+" feet float above a prop: "+sole);
            if(List.of("mallard","puffneck","angry_goose").contains(m.id)) {
                assertEquals(2,m.cubes.stream().filter(c->c.tag().equals("eye_pupil")).count(),m.id+" eyes");
                assertTrue(m.blocks()<=2.05,m.id+" mini proportions");
            }
        }
    }
    @Test void everyCreatureHasIndividualHurtAndDeathClips() throws Exception {
        Set<String> hurts=new HashSet<>(),deaths=new HashSet<>();
        for(var m:models().values()) {
            if(m.id.startsWith("decor_"))continue;
            var hurt=m.anim("hurt");var death=m.anim("death_"+m.id);
            assertNotNull(death,m.id);assertNotNull(hurt,m.id);
            assertTrue(deaths.add(death.length()+":"+new com.google.gson.Gson().toJson(death.bones())),m.id+" repeats death");
            // Different creatures can share an ordinary recoil axis, but the full
            // authored clip (timing, head, jaw and arms) must be individual.
            assertTrue(hurts.add(hurt.length()+":"+new com.google.gson.Gson().toJson(hurt.bones())),m.id+" repeats hurt");
            assertTrue(m.death.stream().anyMatch(s->s.op().equals("anim") && s.str("name","").equals("death_"+m.id)),m.id);
            for(String name:m.attackAnimations()) {
                var a=m.anim(name);if(a==null)continue;
                for(var entry:a.bones().entrySet())if(!entry.getKey().equals("root") && !entry.getKey().matches("^(orb|gem|halo|crystal|book|spark|float|aura).*"))
                    assertNull(entry.getValue().pos(),m.id+" "+name+" translates an attached bone "+entry.getKey());
            }
        }
    }
    private Map<String,ModelRig.Model> models() throws Exception {
        try(var in=getClass().getResourceAsStream("/models.json")) {
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
    @Test void passengerCullingCannotHideDisplacedParts() {
        assertTrue(Displays.outsideDisplayBox(new Matrix4f().translation(0,-2,0),5,6), "feet below a ravager passenger");
        assertTrue(Displays.outsideDisplayBox(new Matrix4f().translation(0,8,0),5,6), "flying death pieces");
        assertTrue(Displays.outsideDisplayBox(new Matrix4f().translation(5,1,0).rotateY(.7f),5,6), "turned parts beyond the side");
        assertFalse(Displays.outsideDisplayBox(new Matrix4f().translation(0,1,0),5,6), "ordinary parts keep culling");
    }
    @Test void eachBossHasItsOwnOpeningWithoutDecorativeRings() throws Exception {
        Set<String> performances=new HashSet<>();
        for(var m:models().values()) {
            if(m.id.startsWith("decor_"))continue;
            var opening=m.anim("opening_"+m.id);
            assertNotNull(opening,m.id);assertFalse(opening.bones().isEmpty(),m.id);
            assertTrue(performances.add(opening.length()+":"+new com.google.gson.Gson().toJson(opening.bones())),m.id+" duplicate performance");
            assertTrue(m.spawn.stream().noneMatch(s->s.num("ring",0)>0),m.id+" ring");
        }
    }
}
