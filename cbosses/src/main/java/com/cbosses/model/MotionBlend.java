package com.cbosses.model;

/** Frame-rate independent transitions, shared by every model. No server state. */
public final class MotionBlend {
    private MotionBlend() {}
    public static float approach(float current, float target, float dt, float seconds) {
        if (dt <= 0) return current;
        return current + (target - current) * (float) (-Math.expm1(-dt / Math.max(0.001f, seconds)));
    }
    public static float turn(float current, float target, float dt) {
        float arc = (float) Math.IEEEremainder(target - current, 360);
        float eased = approach(0, arc, dt, 0.16f);
        float limit = 300 * Math.max(0, dt);
        return Math.max(-limit, Math.min(limit, eased));
    }
    public static float envelope(float time, float length, float in, float out) {
        float p = Math.max(0, Math.min(1, Math.min(time / in, (length-time) / out)));
        return p*p*(3-2*p);
    }
}
