package com.cbosses.util;

import java.util.List;

/** Block-center polygon with boundary inclusion and self-intersection rejection. */
public record Polygon(List<Vertex> vertices) {
    public record Vertex(int x, int z) {}
    public Polygon {
        vertices = List.copyOf(vertices);
        if (vertices.size() < 3 || vertices.size() > 128) throw new IllegalArgumentException("Use 3–128 perimeter points");
        long area = 0;
        for (int i = 0; i < vertices.size(); i++) {
            Vertex a = vertices.get(i), b = vertices.get((i + 1) % vertices.size());
            area += (long) a.x * b.z - (long) b.x * a.z;
            if (a.equals(b)) throw new IllegalArgumentException("Repeated adjacent vertex");
            for (int j = i + 1; j < vertices.size(); j++) {
                if (j == i + 1 || (i == 0 && j == vertices.size() - 1)) continue;
                Vertex c = vertices.get(j), d = vertices.get((j + 1) % vertices.size());
                if (intersects(a,b,c,d)) throw new IllegalArgumentException("Outline crosses itself");
            }
        }
        if (area == 0) throw new IllegalArgumentException("Outline has no area");
    }
    private static long cross(Vertex a, Vertex b, Vertex c) {
        return ((long)b.x-a.x)*((long)c.z-a.z)-((long)b.z-a.z)*((long)c.x-a.x);
    }
    private static boolean on(Vertex a, Vertex b, Vertex p) {
        return cross(a,b,p)==0 && p.x>=Math.min(a.x,b.x) && p.x<=Math.max(a.x,b.x)
                && p.z>=Math.min(a.z,b.z) && p.z<=Math.max(a.z,b.z);
    }
    private static boolean intersects(Vertex a, Vertex b, Vertex c, Vertex d) {
        long abC=cross(a,b,c), abD=cross(a,b,d), cdA=cross(c,d,a), cdB=cross(c,d,b);
        return (Long.signum(abC)*Long.signum(abD)<0 && Long.signum(cdA)*Long.signum(cdB)<0)
                || on(a,b,c) || on(a,b,d) || on(c,d,a) || on(c,d,b);
    }
    public boolean contains(int x, int z) {
        Vertex p = new Vertex(x,z); boolean inside=false;
        for(int i=0,j=vertices.size()-1;i<vertices.size();j=i++) {
            Vertex a=vertices.get(j),b=vertices.get(i);
            if(on(a,b,p)) return true;
            if((a.z>z)!=(b.z>z) && x < (double)(b.x-a.x)*(z-a.z)/(b.z-a.z)+a.x) inside=!inside;
        }
        return inside;
    }
}
