/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { describe, it, expect } from "vitest";
import {
  getPlatform,
  isWindows,
  isMacOS,
  isLinux,
  getPlatformInfo,
  getExecutableExtension
} from "../platform.js";

describe("platform", () => {
  describe("getPlatform", () => {
    it("should return a valid platform", () => {
      const platform = getPlatform();
      expect(["windows", "darwin", "linux"]).toContain(platform);
    });
  });

  describe("platform detection functions", () => {
    it("should have consistent detection", () => {
      // Only one should be true
      const detections = [isWindows(), isMacOS(), isLinux()];
      const trueCount = detections.filter(Boolean).length;
      expect(trueCount).toBe(1);
    });
  });

  describe("getExecutableExtension", () => {
    it("should return a string", () => {
      const ext = getExecutableExtension();
      expect(typeof ext).toBe("string");
      expect([".exe", ""]).toContain(ext);
    });
  });

  describe("getPlatformInfo", () => {
    it("should return comprehensive platform information", () => {
      const info = getPlatformInfo();
      
      expect(info).toHaveProperty("platform");
      expect(info).toHaveProperty("arch");
      expect(info).toHaveProperty("release");
      expect(info).toHaveProperty("version");
      expect(info).toHaveProperty("hostname");
      expect(info).toHaveProperty("cpus");
      expect(info).toHaveProperty("totalmem");
      expect(info).toHaveProperty("freemem");
      
      expect(typeof info.platform).toBe("string");
      expect(typeof info.cpus).toBe("number");
      expect(info.cpus).toBeGreaterThan(0);
    });
  });
});