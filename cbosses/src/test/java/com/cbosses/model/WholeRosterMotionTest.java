package com.cbosses.model;
import org.junit.jupiter.api.Test;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class WholeRosterMotionTest {
 @Test void everyClipEveryBossMatchesDisplayTransformsAndFacesStayExclusive() throws Exception {
  try(var in=getClass().getResourceAsStream("/models.json")) {
   assertNotNull(in);
   for(var model:ModelRig.load(new InputStreamReader(in,StandardCharsets.UTF_8)).values()) {
    for(var anim:model.anims.values()) for(int sample=0;sample<=12;sample++) {
     float time=anim.length()*sample/12;
     var cubes=ModelRig.cubes(model,ModelRig.pose(model,List.of(new ModelRig.Layer(anim,time,1))));
     for(var cube:cubes) {
      var t=Displays.transformation(cube);
      var shown=new Matrix4f().translation(t.getTranslation()).rotate(t.getLeftRotation()).scale(t.getScale()).rotate(t.getRightRotation());
      for(int corner=0;corner<8;corner++) {
       var expected=cube.transformPosition(corner&1,corner>>1&1,corner>>2&1,new Vector3f());
       var actual=shown.transformPosition(corner&1,corner>>1&1,corner>>2&1,new Vector3f());
       assertTrue(Float.isFinite(actual.x)&&Float.isFinite(actual.y)&&Float.isFinite(actual.z),model.id+" "+anim.name());
       assertTrue(expected.distance(actual)<.01f,model.id+" "+anim.name()+" display mismatch");
      }
     }
     if(model.faceOf!=null) {
      model.showFace(cubes,"hurt");
      String face=model.faces.contains("hurt")?"hurt":"idle";
      for(int i=0;i<cubes.length;i++) if(model.faceOf[i]!=null&&!model.faceOf[i].equals(face))
       assertTrue(cubes[i].getScale(new Vector3f()).lengthSquared()<1e-9,model.id+" overlapping face "+i);
     }
    }
   }
  }
 }
 @Test void transitionsAreIndependentOfUpdateFrequencyAndDoNotOvershoot() {
  float a=0,b=0;
  for(int i=0;i<20;i++) a=MotionBlend.approach(a,1,.05f,.18f);
  for(int i=0;i<10;i++) b=MotionBlend.approach(b,1,.1f,.18f);
  assertEquals(a,b,1e-5); assertTrue(a>0&&a<1);
  assertTrue(MotionBlend.turn(179,-179,.15f)>0);
  assertTrue(MotionBlend.turn(-179,179,.15f)<0);
  assertTrue(Math.abs(MotionBlend.turn(0,180,.05f))<=15);
  assertEquals(0,MotionBlend.envelope(0,1,.12f,.18f));
  assertEquals(0,MotionBlend.envelope(1,1,.12f,.18f));
  assertEquals(1,MotionBlend.envelope(.5f,1,.12f,.18f));
 }
 @Test void allApprovedAdditionsHaveDistinctCombatAnimationsAndThemedLifecycle() throws Exception {
  try(var in=getClass().getResourceAsStream("/models.json")) {
   var models=ModelRig.load(new InputStreamReader(in,StandardCharsets.UTF_8));
   for(String id:List.of("millstone_monk","moonwake_manta","thorncoil_basilisk")) {
    var m=models.get(id);assertNotNull(m,id);
    assertTrue(m.attackAnimations().size()>=2,id);
    for(String attack:m.attackAnimations()) assertNotNull(m.anim(attack),id+" "+attack);
    assertTrue(m.spawn.stream().anyMatch(s->s.op().equals("shrink")&&s.at()==0),id);
    assertTrue(m.death.stream().anyMatch(s->s.op().equals("flash")),id);
    assertNotNull(m.anim("opening_"+id));assertNotNull(m.anim("death_"+id));
   }
  }
 }
}
