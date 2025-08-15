/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { describe, it, expect } from "vitest";
import {
  openRouterApiKeySchema,
  apiKeySchema,
  validateJSON,
  sanitizeInput
} from "../validation.js";

describe("validation", () => {
  describe("openRouterApiKeySchema", () => {
    it("should validate correct OpenRouter API keys", () => {
      const validKey = "sk-or-v1-" + "a".repeat(64);
      expect(() => openRouterApiKeySchema.parse(validKey)).not.toThrow();
    });

    it("should reject invalid OpenRouter API keys", () => {
      expect(() => openRouterApiKeySchema.parse("invalid-key")).toThrow();
      expect(() => openRouterApiKeySchema.parse("sk-or-v1-tooshort")).toThrow();
    });
  });

  describe("apiKeySchema", () => {
    it("should validate correct API keys", () => {
      const validKey = "sk-" + "a".repeat(48);
      expect(() => apiKeySchema.parse(validKey)).not.toThrow();
    });

    it("should reject invalid API keys", () => {
      expect(() => apiKeySchema.parse("short")).toThrow(); // Too short (< 8 chars)
      expect(() => apiKeySchema.parse("has invalid@characters")).toThrow(); // Invalid characters
    });
  });

  describe("validateJSON", () => {
    it("should validate correct JSON", () => {
      const result = validateJSON('{"key": "value"}');
      expect(result.success).toBe(true);
      expect(result.data).toEqual({ key: "value" });
    });

    it("should handle invalid JSON", () => {
      const result = validateJSON('{"invalid": json}');
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it("should handle empty string", () => {
      const result = validateJSON("");
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });
  });

  describe("sanitizeInput", () => {
    it("should trim whitespace by default", () => {
      const input = "  normal text  ";
      const result = sanitizeInput(input);
      expect(result).toBe("normal text");
    });

    it("should preserve safe text", () => {
      const input = "This is safe text with numbers 123 and symbols !@#";
      const result = sanitizeInput(input);
      expect(result).toBe(input);
    });

    it("should handle empty input", () => {
      expect(sanitizeInput("")).toBe("");
      expect(sanitizeInput("   ")).toBe("");
    });

    it("should respect trim option", () => {
      const input = "  text  ";
      const result = sanitizeInput(input, { trim: false });
      expect(result).toBe("  text  ");
    });
  });
});