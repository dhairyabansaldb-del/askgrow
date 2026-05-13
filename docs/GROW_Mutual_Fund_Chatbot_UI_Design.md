# UI Design Specification: GROW Mutual Fund AI Companion

## I. Project Overview
This document specifies the user interface and user experience (UI/UX) design for a chatbot-based website designed to answer questions and provide information about GROW Mutual Funds. The design must be a premium, compliant, and user-friendly interface leveraging the design language of `Groww.in` and the chat workflow of modern AI platforms.

## II. Required Aesthetic & Base Layout
* **Aesthetic:** Premium Dark Mode (Black Background). Clean, simple, trustworthy, and compliant.
* **Reference Sites:** ChatGPT, Gemini, Grok (for layout).
* **Base Layout:** A two-panel layout.
    * **Left Sidebar:** Chat history and management.
    * **Right Main Panel:** The active chat interaction area.

## III. Extracted Design Systems (from Groww.in)
Based on an analysis of Groww's visual identity, the following elements will be adapted and refined for this chatbot application.

### A. Color Palette (Groww Dark Mode Context)
* **Background (Canvas):** Pure Black (#000000) or an extremely deep near-black (e.g., #0A0D10) for maximum contrast and focus.
* **Main Container Background:** A slightly lighter dark grey (e.g., #161A1F) for card structures, providing depth against the black canvas. *Reference the rounded card from the prototype screenshot.*
* **Primary Accent:** Groww Green (#00D09C). Use for primary buttons, call-to-actions, and highlights.
* **Primary Text:** Off-white (#F5F7F8).
* **Secondary Text (Muted):** Light Grey (#9BAAB5).
* **Borders & Lines:** Dark Grey (#2C3238).
* **Alert/Disclaimer Accent:** Preserve the prominent Red/Amber from the prototype for compliance features.

### B. Typography
* **Font Family:** A clean, legible sans-serif (e.g., Inter, Public Sans, or Groww's specific brand font if accessible).
* **Hierarchy:**
    * **H1/Header (Chat Title):** Semi-bold, large, primary white text.
    * **H2/Subtitle:** Medium, primary white text.
    * **Body:** Regular, secondary/primary text depending on hierarchy.
    * **Small Text (PII info):** Regular, secondary muted grey.

### C. Iconography
* **Style:** Minimalist, line-based, modern.
* **Usage:** Chat icons, action icons, status icons.

### D. Component Style
* **Corners:** Consistently use rounded corners (similar to the card and input field in the prototype).
* **Buttons:** Pill-shaped or heavily rounded, filled with Groww Green.

## IV. Core Layout & Feature Specification

### 1. The Left Sidebar (ChatGPT/Gemini Style)
* **Aesthetic:** Integrated into the dark theme, using the card background color. A clear boundary line.
* **Elements:**
    * **Header (Top):**
        * **"New Chat" Button:** A prominent, Groww-green accented button with a simple '+' icon.
        * **Groww Logo (Optional):** A small logo/brand indicator at the very top.
    * **Chat History (Scrollable List):** A list of past chat sessions.
        * **Item Format:** Each session titled by the first 3-5 words of the user's first query (e.g., "GROW Flexi Cap Fund...", "How to invest in...").
        * **Active Item State:** A subtle background highlight and a small Groww Green line indicator.
    * **User/Settings (Bottom):**
        * User profile icon or a simple 'Account' button.
        * Settings icon.

### 2. The Main Chat Panel (Right Side)
This panel will integrate the elements seen in the prototype screenshot into a full-page, structured layout.

#### A. Persistent Header Area (Preserve & Adapt)
* **Position:** Fixed at the top of the chat panel.
* **Elements:**
    * **Icon:** The chart icon from the prototype.
    * **Title:** Change to "GROW Mutual Fund Assistant" or "Groww AI Companion". Semibold font.
    * **Status:** Keep the green dot and "Online" text, precisely as styled in the prototype.

#### B. The "NOT FINANCIAL ADVICE" Disclaimer (Crucial Compliance Feature)
* **Aesthetic:** Must be preserved exactly as the red-bordered, high-prominence box from the prototype.
* **Content:** Keep the icon and the exact text: "NOT FINANCIAL ADVICE: This AI assistant provides factual information only. It cannot provide investment recommendations or financial advice."
* **Integration:** Positioned directly below the Persistent Header. It should be visible at all times, perhaps pinned, or appearing as the first message. *This is a key security/compliance design requirement.*

#### C. The Message Stream (Formatting & Styling)
* **Aesthetic:** Clean, with distinct spacing between message bubbles.
* **Bubble Style:**
    * **User Messages:** A simple bubble with a subtle background (e.g., slightly lighter than the card background, #202429) positioned on the right.
    * **Assistant (GROW) Messages:** A simple bubble, or the text presented without a full bubble to keep it clean, positioned on the left. Can be distinguished by a small Groww-green accent line on the left edge.
* **Content Formatting (Adapt from prototype):**
    * For fund lists, preserve the simple list formatting with bullet points. For example:
        > **Dhruv Muchhal** (Semi-bold Name)
        > * GROW Flexi Cap Fund Direct Growth: Dhruv Muchhal and Amit Ganatra (Regular Bullet)
        > ... and so on.

#### D. The Bottom Input Bar (Preserve & Adapt)
* **Position:** Pinned to the bottom of the right chat panel.
* **Elements:**
    * **Input Field:**
        * Rounded corner shape, consistent with Groww style and the prototype.
        * Dark, structured background.
        * **Placeholder Text:** Change to "Ask a question about GROW Mutual Funds...".
        * **Send Icon:** Preserve the paper-plane send icon from the prototype, but color it Groww Green and style it as an interactive button (circular).
    * **Security Disclaimer:** Positioned below the input field, in smaller, lighter text: "Secured with local PII Filtering (PAN/Aadhaar detection active)". This must be kept for transparency and compliance.

### 3. Transition of Key Elements (Summary)
* **Header Title:** HDFC -> GROW.
* **Placeholder Text:** HDFC -> GROW.
* **Color Theme:** The existing dark card from the prototype will be placed on a full black canvas and accented with Groww Green.
* **All other visual elements (PII warning, Status light, red disclaimer box, and specific message formatting) must be preserved in their position and styling, just integrated into the new layout.**

### 4. Interactive States (Antigravity Notes)
* **Buttons:** Apply subtle hover states (e.g., slight background opacity change for the 'New Chat' green button).
* **Chat History:** Highlighting current chat.
* **Loading:** Design a minimal, clean GROW-green loading indicator for the assistant's response phase.

## V. Visual Style Summary (Dark Mode)

A clean, premium, compliant, and highly structured layout centered on the chat interface, integrated into a deep dark canvas with Groww's signature green accents and all compliant safety features preserved.

This design writeup is structured to provide an antigravity frontend developer all necessary assets, hierarchies, and compliance requirements to build a professional-grade GROW Mutual Funds AI Companion.
