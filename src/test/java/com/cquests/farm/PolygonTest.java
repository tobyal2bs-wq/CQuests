package com.cquests.farm;

import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class PolygonTest {
    private static Polygon.Vertex v(int x,int z){return new Polygon.Vertex(x,z);}
    @Test void concaveOutlineIncludesEdgesButNotTheMissingCorner(){
        Polygon p=new Polygon(List.of(v(0,0),v(8,0),v(8,3),v(3,3),v(3,8),v(0,8)));
        assertTrue(p.contains(1,7));assertTrue(p.contains(7,1));assertTrue(p.contains(3,6));
        assertFalse(p.contains(7,7));assertFalse(p.contains(-1,1));
    }
    @Test void reversedWindingAndNegativeCoordinatesWork(){
        Polygon p=new Polygon(List.of(v(-8,-8),v(-8,8),v(8,8),v(8,-8)));
        assertTrue(p.contains(0,0));assertTrue(p.contains(-8,8));assertFalse(p.contains(9,0));
    }
    @Test void malformedOutlinesAreRejected(){
        assertThrows(IllegalArgumentException.class,()->new Polygon(List.of(v(0,0),v(4,4),v(0,4),v(4,0))));
        assertThrows(IllegalArgumentException.class,()->new Polygon(List.of(v(0,0),v(1,1),v(2,2))));
        assertThrows(IllegalArgumentException.class,()->new Polygon(List.of(v(0,0),v(0,0),v(1,2))));
    }
    @Test void inverseSelectionIsBoundedByWorldAndRegionBox(){
        Polygon p=new Polygon(List.of(v(0,0),v(2,0),v(2,2),v(0,2)));
        FarmArea a=new FarmArea("field","world","wg",60,80,p,true,new int[]{-5,60,-5,5,80,5});
        assertTrue(a.candidate("world",4,65,4));assertFalse(a.candidate("world",1,65,1));
        assertFalse(a.candidate("world",8,65,1));assertFalse(a.candidate("world",4,59,4));
        assertFalse(a.candidate("other",4,65,4));
    }
}
