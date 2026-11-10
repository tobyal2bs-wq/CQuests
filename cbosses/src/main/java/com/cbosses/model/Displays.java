package com.cbosses.model;

import org.bukkit.util.Transformation;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Turns a posed cube matrix into what a block display can show (no server registries needed, so tests can use it).
 * A display draws translation x leftRotation x scale x rightRotation, which is a singular value decomposition, so it
 * can show any posed block exactly: stretched, turned, or squashed by a parent bone (a slime's squash used to shear).
 */
public final class Displays {
    private Displays() {}

    /** Vanilla's culling box starts at the passenger origin, not at the
     * transformed cube. Test all eight corners without allocating vectors. */
    public static boolean outsideDisplayBox(Matrix4f m, float halfWidth, float height) {
        float x0=m.m30()+Math.min(0,m.m00())+Math.min(0,m.m10())+Math.min(0,m.m20());
        float x1=m.m30()+Math.max(0,m.m00())+Math.max(0,m.m10())+Math.max(0,m.m20());
        float y0=m.m31()+Math.min(0,m.m01())+Math.min(0,m.m11())+Math.min(0,m.m21());
        float y1=m.m31()+Math.max(0,m.m01())+Math.max(0,m.m11())+Math.max(0,m.m21());
        float z0=m.m32()+Math.min(0,m.m02())+Math.min(0,m.m12())+Math.min(0,m.m22());
        float z1=m.m32()+Math.max(0,m.m02())+Math.max(0,m.m12())+Math.max(0,m.m22());
        return x0 < -halfWidth || x1 > halfWidth || y0 < 0 || y1 > height || z0 < -halfWidth || z1 > halfWidth;
    }

    public static Transformation transformation(Matrix4f m) {
        Vector3f t = m.getTranslation(new Vector3f());
        Vector3f c0 = new Vector3f(m.m00(), m.m01(), m.m02()), c1 = new Vector3f(m.m10(), m.m11(), m.m12()), c2 = new Vector3f(m.m20(), m.m21(), m.m22());
        float l0 = c0.length(), l1 = c1.length(), l2 = c2.length();
        if (l0 < 1e-5f || l1 < 1e-5f || l2 < 1e-5f) return new Transformation(t, new Quaternionf(), new Vector3f(l0, l1, l2), new Quaternionf());
        // Almost every block is only turned and stretched (its edges stay square): the rotation is then simply the
        // columns over their lengths. That keeps one rotation per block from frame to frame, so the client's smooth
        // movement between frames never spins a block the long way round.
        if (Math.abs(c0.dot(c1)) < 1e-3f * l0 * l1 && Math.abs(c0.dot(c2)) < 1e-3f * l0 * l2 && Math.abs(c1.dot(c2)) < 1e-3f * l1 * l2) {
            Quaternionf q = new Quaternionf().setFromNormalized(new Matrix3f(c0.x / l0, c0.y / l0, c0.z / l0, c1.x / l1, c1.y / l1, c1.z / l1, c2.x / l2, c2.y / l2, c2.z / l2));
            if (Float.isFinite(q.w) && Float.isFinite(q.x)) return new Transformation(t, q, new Vector3f(l0, l1, l2), new Quaternionf());
        }
        // A block squashed by a parent bone while turned is skewed: show it exactly with both rotations (an SVD).
        float[][] a = {{m.m00(), m.m10(), m.m20()}, {m.m01(), m.m11(), m.m21()}, {m.m02(), m.m12(), m.m22()}}; // a[row][col]
        // B = A^T A, symmetric; its eigenvectors are the right singular vectors
        double[][] b = new double[3][3];
        for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) { double s = 0; for (int k = 0; k < 3; k++) s += a[k][i] * a[k][j]; b[i][j] = s; }
        double[][] v = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
        for (int sweep = 0; sweep < 12; sweep++) {
            double off = b[0][1] * b[0][1] + b[0][2] * b[0][2] + b[1][2] * b[1][2];
            if (off < 1e-14) break;
            for (int p = 0; p < 2; p++) for (int q = p + 1; q < 3; q++) {
                if (Math.abs(b[p][q]) < 1e-12) continue;
                double theta = (b[q][q] - b[p][p]) / (2 * b[p][q]);
                double tt = Math.signum(theta) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
                if (theta == 0) tt = 1;
                double c = 1 / Math.sqrt(tt * tt + 1), s = tt * c;
                for (int k = 0; k < 3; k++) { double bkp = b[k][p], bkq = b[k][q]; b[k][p] = c * bkp - s * bkq; b[k][q] = s * bkp + c * bkq; }
                for (int k = 0; k < 3; k++) { double bpk = b[p][k], bqk = b[q][k]; b[p][k] = c * bpk - s * bqk; b[q][k] = s * bpk + c * bqk; }
                for (int k = 0; k < 3; k++) { double vkp = v[k][p], vkq = v[k][q]; v[k][p] = c * vkp - s * vkq; v[k][q] = s * vkp + c * vkq; }
            }
        }
        float[] sig = new float[3];
        float[][] u = new float[3][3];
        for (int j = 0; j < 3; j++) {
            sig[j] = (float) Math.sqrt(Math.max(0, b[j][j]));
            for (int i = 0; i < 3; i++) { double s = 0; for (int k = 0; k < 3; k++) s += a[i][k] * v[k][j]; u[i][j] = sig[j] > 1e-6f ? (float) (s / sig[j]) : 0; }
        }
        if (sig[0] < 1e-5f || sig[1] < 1e-5f || sig[2] < 1e-5f)   // a shrunk-away block: just its size
            return new Transformation(t, new Quaternionf(), m.getScale(new Vector3f()), new Quaternionf());
        // keep both rotations proper (no mirror)
        if (det(v) < 0) for (int i = 0; i < 3; i++) v[i][2] = -v[i][2];
        for (int i = 0; i < 3; i++) { double s = 0; for (int k = 0; k < 3; k++) s += a[i][k] * v[k][2]; u[i][2] = (float) (s / sig[2]); }
        if (det(u) < 0) { sig[2] = -sig[2]; for (int i = 0; i < 3; i++) u[i][2] = -u[i][2]; }
        Matrix3f um = new Matrix3f(u[0][0], u[1][0], u[2][0], u[0][1], u[1][1], u[2][1], u[0][2], u[1][2], u[2][2]);
        Matrix3f vt = new Matrix3f((float) v[0][0], (float) v[0][1], (float) v[0][2], (float) v[1][0], (float) v[1][1], (float) v[1][2],
                (float) v[2][0], (float) v[2][1], (float) v[2][2]);   // column-major args: V^T
        Quaternionf left = new Quaternionf().setFromNormalized(um), right = new Quaternionf().setFromNormalized(vt);
        if (!Float.isFinite(left.w) || !Float.isFinite(right.w)) return new Transformation(t, new Quaternionf(), m.getScale(new Vector3f()), new Quaternionf());
        return new Transformation(t, left, new Vector3f(sig[0], sig[1], sig[2]), right);
    }

    private static double det(double[][] x) {
        return x[0][0] * (x[1][1] * x[2][2] - x[1][2] * x[2][1]) - x[0][1] * (x[1][0] * x[2][2] - x[1][2] * x[2][0]) + x[0][2] * (x[1][0] * x[2][1] - x[1][1] * x[2][0]);
    }

    private static double det(float[][] x) {
        return x[0][0] * (x[1][1] * x[2][2] - x[1][2] * x[2][1]) - x[0][1] * (x[1][0] * x[2][2] - x[1][2] * x[2][0]) + x[0][2] * (x[1][0] * x[2][1] - x[1][1] * x[2][0]);
    }
}
