package com.cquests.progression;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class LevelCurveTest {
    private final LevelCurve curve=new LevelCurve(100,38_880_000,2.2);
    @Test void everyLevelBoundaryAndProgressStayConsistent(){
        assertEquals(1,curve.level(0));
        for(int n=2;n<=100;n++){
            assertTrue(curve.threshold(n)>curve.threshold(n-1));
            assertEquals(n,curve.level(curve.threshold(n)));
            assertEquals(n-1,curve.level(curve.threshold(n)-1));
            assertEquals(n==100?1:0,curve.progress(curve.threshold(n)),1e-9);
        }
    }
    @Test void maxLevelCapsAndHasNoRemainingXp(){
        assertEquals(100,curve.level(Long.MAX_VALUE));assertEquals(0,curve.remaining(Long.MAX_VALUE));
        assertEquals(1,curve.progress(Long.MAX_VALUE));assertEquals(38_880_000,curve.threshold(1000));
    }
    @Test void invalidConfigurationCannotMakeNanProgress(){
        assertThrows(IllegalArgumentException.class,()->new LevelCurve(100,100,Double.NaN));
        assertThrows(IllegalArgumentException.class,()->new LevelCurve(1,100,2));
    }
    @Test void smallAdminConfiguredCurveStillRequiresXpForEveryLevel(){
        LevelCurve small=new LevelCurve(100,100,8);
        assertEquals(1,small.level(0));for(int n=2;n<=100;n++)assertTrue(small.threshold(n)>small.threshold(n-1));
    }
}
