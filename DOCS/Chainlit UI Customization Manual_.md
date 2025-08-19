

# **The Definitive Guide to Chainlit UI Customization**

## **Introduction: The Philosophy of Chainlit Customization**

Chainlit provides a powerful and layered framework for customizing the user interface (UI) of conversational AI applications. This approach allows developers to move progressively from simple configuration-based tweaks to deep, code-level modifications, ensuring that the level of effort matches the desired level of customization. Understanding this hierarchy is fundamental to effectively tailoring the look, sound, and behavior of a Chainlit application to meet specific branding and functional requirements.

The customization capabilities can be understood as a series of layers, each offering greater control than the last:

1. **Configuration (config.toml):** The highest level of control, managed through the .chainlit/config.toml file. This file acts as the central hub for enabling features, setting application metadata, and making simple theme adjustments.1  
2. **Asset-Based Branding (/public):** This layer involves replacing default assets with custom ones. By placing correctly named files in the /public directory, developers can change logos, favicons, and chat avatars.2  
3. **Declarative Theming (theme.json):** For comprehensive visual overhauls, Chainlit uses a theme.json file. This allows for the definition of complete color palettes, fonts, and other stylistic variables for both light and dark modes, based on a modern CSS variable system.4  
4. **Granular Styling (Custom CSS):** When the theming system is insufficient, developers can inject a custom CSS stylesheet to override any default style, providing pixel-perfect control over every element in the UI.5  
5. **Full Component Control (Custom JS/JSX):** The deepest level of customization involves injecting custom JavaScript or even rendering entirely new, interactive UI components built with JSX (React), which can communicate with the Python backend.6

This guide will deconstruct each of these layers, providing an exhaustive manual for customizing the three core aspects of the user experience:

* **Look:** The visual appearance of the application, from colors and fonts to logos and the layout of chat messages. This is achieved through the combined use of config.toml, theme.json, custom assets, and CSS.  
* **Sound:** This aspect pertains specifically to the ability to display playable audio files as content within the chat interface using the cl.Audio element. The framework does not currently provide for the customization of system-level UI sounds (e.g., message notification chimes).8  
* **Acts:** The interactive behavior of the application. This ranges from simple UI behaviors like collapsing large messages to complex, custom-built interactive elements, clickable action buttons, and user-selectable chat profiles, all of which are orchestrated from the Python backend but manifest in the front-end UI.

Throughout this customization journey, the config.toml file serves as the primary orchestrator, acting as the entry point for enabling and configuring most of the visual and behavioral modifications discussed in this manual.

## **Part 1: The Customization Hub: A Complete Guide to config.toml**

The .chainlit/config.toml file is the cornerstone of any customization effort. Created upon project initialization, it serves as the central configuration point for UI settings, feature flags, and project metadata.1 A thorough understanding of its parameters is the first step toward mastering the Chainlit UI. This file is organized into sections, with the

\[UI\] section being the most critical for visual and behavioral customization.

### **1.1. The \[UI\] Section: Master Reference**

The \[UI\] section of the config.toml file is the primary control panel for high-level UI settings. It governs everything from the application's name and description to the behavior of the chat interface and the loading of custom assets like CSS and JavaScript. The following table consolidates all available parameters within the \[UI\] section, providing a single, authoritative reference.

| Parameter | Data Type | Default Value | Detailed Description & Purpose | Source(s) |
| :---- | :---- | :---- | :---- | :---- |
| name | string | "My Chatbot" | Sets the name of the application and the chatbot. This value is used in the UI header and browser tab title. | 9 |
| description | string | "" | Populates the \<meta name="description"\> HTML tag. This is important for search engine optimization (SEO) and for providing context when the application link is shared. | 9 |
| cot | Literal\['hidden', 'tool\_call', 'full'\] | "full" | Controls the visibility of the Chain of Thought (COT). "full" shows all steps, "tool\_call" shows only tool interactions, and "hidden" conceals the agent's reasoning process from the user. | 9 |
| default\_collapse\_content | boolean | true | If true, large blocks of text content within messages are automatically collapsed to maintain a concise and clean UI. Users can expand the content manually. | 9 |
| default\_expand\_messages | boolean | false | If true, nested sub-messages are expanded by default. The default behavior (false) is to hide them until the user expands the parent message. | 9 |
| github | string | "" | A URL to a GitHub repository. If provided, a GitHub icon linking to this URL will be displayed in the application header. If left empty, the link defaults to the Chainlit repository. | 9 |
| custom\_css | string | "" | The path to a custom CSS file. This can be a local path relative to the /public directory (e.g., "/public/stylesheet.css") or an external URL. | 5 |
| custom\_js | string | "" | The path to a custom JavaScript file. Similar to custom\_css, this can be a local path within /public or an external URL. | 6 |
| login\_page\_image | string | "" | The path or URL to a custom background image for the login page (if authentication is enabled). | 2 |
| login\_page\_image\_filter | string | "" | Applies a Tailwind CSS filter class (e.g., "brightness-50 grayscale") to the login page background image in both light and dark modes. | 2 |
| login\_page\_image\_dark\_filter | string | "" | Applies a Tailwind CSS filter class specifically to the login page background image when the UI is in dark mode (e.g., "contrast-200 blur-sm"). | 2 |

### **1.2. Configuring Core UI Behavior**

Beyond simple branding, the parameters in config.toml allow for significant control over the application's fundamental behavior and information architecture.

#### **Application Identity**

Setting the name and description parameters is the most basic form of customization. The name directly replaces the default "My Chatbot" text in the UI, immediately establishing the application's identity. The description is not visible in the UI itself but is crucial for how the application is represented on the web, influencing search engine results and link previews.9

#### **Controlling Information Density**

The chat interface can quickly become cluttered, especially when dealing with long responses or complex, multi-step processes. The default\_collapse\_content and default\_expand\_messages parameters provide control over this information density. By default, default\_collapse\_content is true, which helps keep threads concise by hiding the bulk of large text elements until a user chooses to see more. Conversely, default\_expand\_messages is false by default, hiding the sub-steps of a message to present a high-level summary first. Adjusting these booleans allows developers to tailor the default verbosity of the interface to their specific use case—a highly technical debugging tool might benefit from expanding everything by default, while a simple customer-facing chatbot would benefit from keeping things collapsed and clean.9

#### **Managing Agent Transparency**

A key feature of many advanced agents is their ability to show their "reasoning" process, often called a Chain of Thought (COT). The cot parameter provides granular control over how much of this process is exposed to the end-user.9 This is not merely a cosmetic setting; it directly impacts the user's trust and understanding of the agent's capabilities.

* "full": The default setting provides maximum transparency, showing every step, thought, and tool call the agent made to arrive at its conclusion. This is invaluable for debugging and for users who want to verify the agent's logic.  
* "tool\_call": This setting strikes a balance, hiding the internal "thoughts" of the agent but still showing when it interacts with external tools (e.g., APIs, databases). This confirms that the agent is taking action without overwhelming the user with verbose reasoning.  
* "hidden": This setting provides the most streamlined, "magical" user experience by completely hiding the reasoning process. The user only sees the initial query and the final answer. This is best suited for simple applications where the internal process is irrelevant or could be confusing to the user.10

### **1.3. The Duality of Theming: config.toml vs. theme.json**

Chainlit's documentation reveals two distinct methods for theming the application, which points to a layered front-end architecture. Understanding the difference between these two paths is crucial for choosing the right tool for the job.

One path involves using the \[UI.theme\] section within config.toml. The documentation notes that these settings are for overriding the "default MUI light/dark theme," suggesting this method targets a Material-UI-based component layer.9 This is likely a simpler, perhaps legacy, system designed for quick and easy color adjustments.

The second, more modern path is to use a /public/theme.json file. This method is based on CSS variables and is explicitly linked to the Shadcn/UI and Tailwind CSS ecosystem, which offers far more comprehensive control over the application's entire design system.4

For simple color tweaks, the config.toml approach may be sufficient. However, for a complete brand overhaul or for designs that require precise control over all UI elements, the theme.json method is the more powerful and recommended approach.

#### **Path 1 (Simple Overrides via config.toml)**

To make quick changes to the primary colors and surfaces, one can add a \[UI.theme\] section to config.toml. This section can contain subsections for light and dark modes.

Example configuration for simple theme overrides in config.toml:

Ini, TOML

\[UI.theme.light\]  
\#background \= "\#FAFAFA"  
\#paper \= "\#FFFFFF"  
\[UI.theme.light.primary\]  
\#main \= "\#F80061"  
\#dark \= "\#980039"  
\#light \= "\#FFE7EB"

\[UI.theme.dark\]  
\#background \= "\#FAFAFA"  
\#paper \= "\#FFFFFF"  
\[UI.theme.dark.primary\]  
\#main \= "\#F80061"  
\#dark \= "\#980039"  
\#light \= "\#FFE7EB"

By uncommenting and modifying these hexadecimal color values, a developer can quickly change the application's core color scheme without needing to create additional files.9

#### **Path 2 (Advanced Theming via theme.json)**

The more robust method for theming is to create a theme.json file. This approach offers control over a much wider array of design tokens and is the foundation for deep visual customization. This method will be explored in exhaustive detail in Part 3 of this guide.

## **Part 2: Visual Identity: Branding, Avatars, and Login**

Establishing a unique visual identity is crucial for any application. Chainlit facilitates this through a straightforward, asset-based approach centered around the /public directory. By placing correctly named image files in this directory, developers can seamlessly replace default branding elements with their own.

### **2.1. The public Directory: Your Asset Staging Area**

The /public directory is a special folder that should be located at the root of the Chainlit project, next to the main application script. Its contents are made directly accessible by the web server that runs the Chainlit front end. This makes it the designated staging area for all custom static assets, including logos, favicons, avatars, CSS stylesheets, JavaScript files, and custom JSX components.2 Understanding this convention is key, as nearly every file-based customization will involve placing assets into this folder or one of its subdirectories.

### **2.2. Deploying Custom Logos and Favicons**

Replacing the default Chainlit logo and browser favicon is a primary step in branding an application.

#### **Logo Implementation**

Chainlit's UI supports both light and dark themes, and it expects separate logo files to ensure visibility in both modes. To implement a custom logo, two files must be created and placed in the root of the /public directory:

* logo\_dark.png: This logo will be displayed when the user has the dark theme active. It should be designed to be clearly visible on dark backgrounds.  
* logo\_light.png: This logo will be displayed when the light theme is active and should be visible on light backgrounds.

Once these two files are in place, restarting the application will cause them to be automatically detected and displayed in the UI header.2

#### **Favicon Implementation**

The favicon, the small icon displayed in the browser tab, can also be customized. To do this, place an image file named favicon in the /public directory. While the documentation does not specify an extension, standard web formats like favicon.png or favicon.ico are conventional choices.2

#### **Troubleshooting Asset Caching**

A common point of friction when updating logos and favicons is browser caching. Browsers aggressively cache these assets to improve performance. If changes are not visible after restarting the application, it is almost always necessary to perform a hard refresh or completely clear the browser's cache to force it to download the new files.2

### **2.3. Personalizing Chat Avatars**

Avatars give personality to the participants in a conversation, distinguishing between the user and various assistants or agents. Chainlit has moved from a programmatic approach (cl.Avatar, which is now deprecated) to a more robust and persistent file-based system.11

#### **The Modern Avatar System**

The current method for setting custom avatars is to place image files in a specific subdirectory: /public/avatars/. Chainlit will automatically look in this folder for an avatar that matches the author name of a given message.3

#### **File Naming Convention**

The key to this system is the file naming convention. The image file must be named after the author of the message, converted to a web-safe format. For example, if a message is sent with the author name "My Assistant", the application will look for an image at /public/avatars/my\_assistant.png (or my-assistant.png). The system is flexible regarding separators, typically handling spaces converted to hyphens or underscores.3

The expected directory structure is as follows:

public/  
└── avatars/  
    └── my\_assistant.png  
    └── data\_analyst.png

#### **Default Behavior**

If a message is sent by an author for whom no corresponding avatar image is found in the /public/avatars/ directory, the UI will use the application's favicon as the default avatar for that author. This ensures that every message has an associated icon.3

### **2.4. Customizing the Login Page**

For applications that require authentication, the login page is the user's first visual contact with the brand. Chainlit provides options in config.toml to customize its background.

#### **Background Image**

The login\_page\_image parameter in the \[UI\] section of config.toml allows for the specification of a custom background image. This value can be a local path to an image within the /public directory (e.g., "/public/custom-background.jpg") or a full external URL to an image hosted elsewhere.2

#### **Image Filters**

To improve the readability of the login form over the background image or to better align the image with the brand's aesthetic, CSS filters can be applied. The config.toml file provides two parameters for this, which accept Tailwind CSS filter utility classes:

* login\_page\_image\_filter: Applies filters in both light and dark modes. Example: "brightness-50 grayscale".  
* login\_page\_image\_dark\_filter: Applies filters that are active *only* when the dark theme is enabled, allowing for different visual treatments. Example: "contrast-200 blur-sm".

Example configuration in config.toml:

Ini, TOML

\[UI\]  
\# Custom login page image, relative to public directory or external URL  
login\_page\_image \= "/public/custom-background.jpg"

\# Custom login page image filter (Tailwind internal filters)  
login\_page\_image\_filter \= "brightness-50"

\# Custom login page image filter for dark mode  
login\_page\_image\_dark\_filter \= "brightness-75"

These settings provide a simple yet powerful way to create a fully branded and professional-looking entry point for users.2

## **Part 3: Advanced Visuals: Theming, Fonts, and Custom CSS**

While asset replacement and simple configuration handle basic branding, achieving a truly unique and polished look requires deeper control over the application's design system. Chainlit provides three powerful mechanisms for this: a comprehensive theming system via theme.json, custom font integration, and the surgical precision of custom CSS.

### **3.1. The theme.json Deep Dive: Creating Bespoke Palettes**

The theme.json file is the modern and recommended method for implementing a complete visual theme. It operates by defining a set of CSS variables that the entire front-end component library uses for styling. This approach is more flexible and powerful than the simple color overrides available in config.toml.4

#### **File Creation and Structure**

To begin, a file named theme.json must be created in the /public directory. The root of this JSON object contains two main keys: custom\_fonts (an array) and variables (an object). The variables object is further divided into light and dark objects, allowing for the definition of distinct color palettes and styles for each mode.4

#### **The HSL Color Requirement**

A critical requirement of the theme.json file is that all color values **must** be specified in HSL (Hue, Saturation, Lightness) format, without the hsl() wrapper. For example, white is not "\#FFFFFF" but "0 0% 100%". This is mandatory. Developers can use online tools to convert from other formats like Hex or RGB to the required HSL string format.4

#### **theme.json CSS Variable Reference**

The documentation directs users to the Shadcn UI documentation to understand the role of each CSS variable. However, to provide a more self-contained and efficient development experience, the following table outlines the most important variables and their functions.

| CSS Variable | Description | Scope |
| :---- | :---- | :---- |
| \--background | The main background color of the application content area. | Light/Dark |
| \--foreground | The default color for text and icons. | Light/Dark |
| \--card | The background color for card-like elements, such as message bubbles. | Light/Dark |
| \--card-foreground | The text color used inside card elements. | Light/Dark |
| \--primary | The primary accent color, used for buttons, links, and other interactive elements. | Light/Dark |
| \--primary-foreground | The color of text and icons placed on top of a primary-colored background. | Light/Dark |
| \--secondary | A secondary accent color, often used for less prominent interactive elements. | Light/Dark |
| \--secondary-foreground | The text color for secondary-colored backgrounds. | Light/Dark |
| \--accent | An accent color typically used for hover states or subtle highlights. | Light/Dark |
| \--accent-foreground | The text color for accent-colored backgrounds. | Light/Dark |
| \--destructive | A color used to indicate destructive actions, such as delete buttons (typically red). | Light/Dark |
| \--border | The color for borders on elements like input fields and cards. | Light/Dark |
| \--input | The background color for input fields. | Light/Dark |
| \--ring | The color of the focus ring that appears around interactive elements. | Light/Dark |
| \--radius | The default border-radius for most elements, controlling the roundness of corners (e.g., "0.75rem"). | Both |
| \--sidebar-background | The background color of the sidebar. | Light/Dark |
| \--sidebar-foreground | The text color used in the sidebar. | Light/Dark |

By defining these variables within the light and dark objects in theme.json, a developer can exercise complete control over the application's color scheme.4

### **3.2. Integrating Custom Typography**

Fonts are a cornerstone of brand identity. The theme.json file provides a straightforward way to integrate custom web fonts.

This is a two-step process:

1. **Link the Font Stylesheet:** In the custom\_fonts array at the top level of theme.json, add the URL to the font's CSS file. This is typically a URL provided by a service like Google Fonts.4  
2. **Apply the Font:** Inside the light and dark variable objects, set the \--font-sans (for sans-serif text) and/or \--font-mono (for monospaced text) variables to use the newly imported font family.

Example theme.json for adding the "Inter" font:

JSON

{  
  "custom\_fonts": \[  
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700\&display=swap"  
  \],  
  "variables": {  
    "light": {  
      "--font-sans": "'Inter', sans-serif",  
      //... other light theme variables  
    },  
    "dark": {  
      "--font-sans": "'Inter', sans-serif",  
      //... other dark theme variables  
    }  
  }  
}

### **3.3. Surgical Styling with Custom CSS**

For modifications that go beyond what the theming system can offer, or to target a very specific element for a style change, custom CSS is the ultimate tool. It allows for overriding any style on any element in the UI.

The documentation explicitly states that a comprehensive list of all CSS classes is not provided, and instead encourages developers to use their browser's Web Inspector to find the classes they wish to override.5 This approach, while requiring some front-end knowledge, is more robust and future-proof than relying on a static list of classes that could change between framework versions.

#### **Enabling Custom CSS**

To enable this feature, set the custom\_css parameter in the \[UI\] section of config.toml. The value should be the path to a CSS file, either locally in the /public directory (e.g., "/public/stylesheet.css") or an external URL.5

#### **Practical Tutorial: Finding and Overriding a Class**

The process of using the Web Inspector for custom styling is a powerful skill. Here is a practical workflow:

1. **Run the Chainlit Application:** Start the application so it is running and accessible in a web browser.  
2. **Open Developer Tools:** Open the browser's Developer Tools. This is typically done by pressing F12 or right-clicking on the page and selecting "Inspect."  
3. **Select the Target Element:** Use the element selection tool (often an icon of a cursor in a box) to click directly on the UI element you want to modify. This will highlight the corresponding HTML in the "Elements" panel of the developer tools.  
4. **Identify the CSS Class:** In the "Elements" panel, examine the class attribute of the selected HTML element. In the "Styles" panel, you can see all the CSS rules that apply to that element and the class names they target.  
5. **Write an Override Rule:** In your custom stylesheet.css file, write a new CSS rule targeting the class you identified. To ensure your rule takes precedence, you may need to use a more specific selector or the \!important flag (though the latter should be used sparingly). For example, to change the color of message author names, one might inspect the element and find a class like message-author. The custom CSS would then be:

.message-author {  
color: \#F80061\!important;  
}  
\`\`\`  
6\. Restart and Refresh: After saving the CSS file, restart the Chainlit application. As with other assets, it may be necessary to clear the browser cache to see the changes take effect.5

## **Part 4: Interactive Elements: Customizing UI Actions and Behavior**

A chatbot's UI is more than just a static display of text; it is an interactive surface. Chainlit provides several Python-native abstractions that allow developers to create dynamic and interactive behaviors, such as clickable buttons (Actions) and selectable assistant configurations (Chat Profiles).

### **4.1. Creating Clickable Actions**

Actions are clickable buttons that can be attached to any message. When a user clicks an Action, it triggers a specific function on the Python backend, enabling a direct and intuitive way for users to guide the conversation or execute commands.

#### **Defining an Action**

An action is an instance of the cl.Action class. Key attributes include:

* name: A unique string identifier for the action. This name is used to link the button to its corresponding callback function.  
* label: The text displayed on the button for the user to see.  
* icon: An optional icon name from the [Lucide icon library](https://lucide.dev/icons/) to display next to the label.  
* payload: A dictionary containing any data that should be sent back to the server when the action is clicked. This is useful for passing context.  
* tooltip: A string that appears when the user hovers over the action button.12

#### **Attaching to a Message**

Actions are sent to the UI by passing a list of cl.Action objects to the actions parameter of a cl.Message.13

#### **Handling the Callback**

To make an action functional, a corresponding callback function must be defined in the Python code. This is done using the @cl.action\_callback decorator, passing the name of the action as an argument. The decorated function will be executed when the user clicks the button, and it receives the cl.Action object (including its payload) as an argument.13

Example of creating and handling an action:

Python

import chainlit as cl

@cl.on\_chat\_start  
async def start():  
    \# Sending an action button within a chatbot message  
    actions \=  
    await cl.Message(  
        content="I have received your file. Click the button to start processing.",  
        actions=actions  
    ).send()

@cl.action\_callback("process\_data")  
async def on\_action(action: cl.Action):  
    \# The action's payload is accessible here  
    print(f"Action clicked\! Payload: {action.payload}")  
    await cl.Message(content="Processing has started...").send()  
    \# Here you would add the actual data processing logic  
    await action.remove() \# Optionally remove the button after it's clicked

### **4.2. Offering User Choice with Chat Profiles**

Chat Profiles provide a way for users to choose from a list of predefined assistant configurations at the beginning of a new chat. This is extremely useful for applications that can operate in different modes or use different underlying models (e.g., a creative writing assistant vs. a technical coding assistant).14

#### **Implementation**

Chat Profiles are defined using the @cl.set\_chat\_profiles decorator on an asynchronous function. This function must return a list of cl.ChatProfile instances. Each cl.ChatProfile can be configured with:

* name: The name of the profile, displayed to the user.  
* markdown\_description: A description of the profile, which supports Markdown for rich formatting. This is where the purpose of the profile can be explained.  
* icon: A URL to an icon for the profile.15

When a user selects a profile, the on\_chat\_start function is re-triggered, and the selected profile name is available in the user session via cl.user\_session.get("chat\_profile").

Example of setting up chat profiles:

Python

import chainlit as cl

@cl.set\_chat\_profiles  
async def chat\_profile():  
    return

#### **Conditional Profiles**

The function decorated with @cl.set\_chat\_profiles can accept the current\_user object as an argument (if authentication is enabled). This allows for the creation of conditional chat profiles, where the available options can be tailored based on the user's role or permissions. For example, an "ADMIN" user might see an experimental or debugging profile that is hidden from regular users.15

### **4.3. Exposing User-Modifiable Chat Settings**

For even greater in-session interactivity, Chainlit provides Chat Settings. This feature, when configured, adds a settings button to the chat input bar. Clicking this button opens a modal panel where the user can modify predefined settings (e.g., temperature, model parameters) during the conversation. When the user updates these settings, an event is sent back to the Chainlit server, allowing the application to react to the changes in real-time.16

The provided documentation confirms the existence and UI effect of this feature but does not contain the specific API for its implementation. Developers seeking to use this feature should consult the official Chainlit API reference for the classes and decorators required to define and handle chat settings.

## **Part 5: Extending the UI with Code: JavaScript and Custom JSX Components**

For developers who need to push beyond the boundaries of the standard UI, Chainlit offers two powerful escape hatches: the ability to inject arbitrary client-side JavaScript and, most significantly, the ability to render entirely custom UI components built with JSX (React).

### **5.1. Injecting Client-Side Logic with Custom JavaScript**

For general-purpose client-side tasks, such as integrating a third-party analytics service (like Google Analytics), adding custom event listeners, or performing minor DOM manipulations not easily achievable with CSS, a custom JavaScript file can be injected into the application.

This is enabled by setting the custom\_js parameter in the \[UI\] section of config.toml. The value can be a local path within the /public directory (e.g., "/public/my\_script.js") or an external URL to a script file. Once the configuration is updated and the application is restarted, the script will be loaded and executed on the client side.6

### **5.2. Building Custom UI Components with JSX**

This is the pinnacle of Chainlit UI customization. The cl.CustomElement class allows developers to render their own React components, written in JSX, directly within the chat interface. This opens the door to creating rich, interactive, and domain-specific UI elements that go far beyond simple text and buttons.

#### **The Core Concept**

The system works by linking a Python object to a JSX file. In the Python code, an instance of cl.CustomElement is created. In the front-end project, a corresponding .jsx file is placed in the /public/elements/ directory. The name attribute of the cl.CustomElement must match the filename of the JSX component (without the extension).7

#### **File Structure and JSX Definition**

* **Location:** A custom component named "StatusCard" would require a file at /public/elements/StatusCard.jsx.  
* **Python Call:** cl.CustomElement(name="StatusCard", props={...}).  
* **JSX Requirements:** The .jsx file must have a default export which is a React functional component. Component props are injected globally by the Chainlit runtime and should **not** be passed as a function argument. Styling is done using standard Tailwind CSS classes, which have access to the CSS variables defined in theme.json.7

#### **The Python-to-JSX Data Bridge**

Dynamic data is passed from the Python backend to the front-end component via the props attribute of the cl.CustomElement constructor. This attribute accepts a dictionary, which is then made available as a global props object within the JSX component's scope.7

#### **Custom Element JavaScript API Reference**

To make these components truly interactive, Chainlit exposes a global JavaScript API within the custom element's environment. This API allows the front-end component to communicate back with the Chainlit application and the Python backend.

| API Function | Signature | Description |
| :---- | :---- | :---- |
| updateElement | (nextProps: Record\<string, any\>) \=\> Promise\<{success: boolean}\> | Updates the props of the current element and triggers a re-render. This is for client-side state changes. |
| deleteElement | () \=\> Promise\<{success: boolean}\> | Removes the custom element from the UI entirely. |
| callAction | (action: {name: string, payload: Record\<string, unknown\>}) \=\> Promise\<{success: boolean}\> | Calls a Python function decorated with @cl.action\_callback, passing a name and payload. This is the primary way for a custom component to trigger backend logic. |
| sendUserMessage | (message: string) \=\> void | Sends a new message to the chat as if the user had typed it. |

This API is what transforms a static display into a living part of the application.7

#### **End-to-End Example: Building a Dynamic Status Card**

This example demonstrates how to create a custom component that displays the status of a ticket.

1. **Python (app.py):** The backend code fetches data and sends the custom element.  
   Python  
   import chainlit as cl

   @cl.on\_message  
   async def on\_message(msg: cl.Message):  
       \# In a real app, this data would come from an API call  
       ticket\_props \= {  
           "title": "Fix Authentication Bug",  
           "status": "in-progress",  
           "assignee": "Sarah Chen"  
       }

       ticket\_element \= cl.CustomElement(  
           name="TicketStatusCard",   
           props=ticket\_props,  
           display="inline" \# Can be "inline", "side", or "page"  
       )

       await cl.Message(  
           content="Here is the ticket information:",  
           elements=\[ticket\_element\]  
       ).send()

2. **JSX (/public/elements/TicketStatusCard.jsx):** The front-end component that renders the props.  
   JavaScript  
   // Note: This is JSX, not TSX. No type annotations.  
   // Props are globally available, not passed as an argument.  
   // We can import from a limited set of allowed packages like lucide-react.  
   import { User } from 'lucide-react';

   export default function TicketStatusCard() {  
     // Helper to determine color based on status  
     const getStatusColor \= (status) \=\> {  
       if (status \=== 'in-progress') return 'bg-blue-500';  
       if (status \=== 'resolved') return 'bg-green-500';  
       return 'bg-gray-500';  
     };

     return (  
       \<div className\="p-4 border rounded-lg shadow-md bg-card text-card-foreground max-w-sm"\>  
         \<div className\="flex justify-between items-center mb-2"\>  
           \<h3 className\="font-bold text-lg"\>{props.title}\</h3\>  
           \<span className\={\`px-2 py-1 text-xs font-semibold text-white rounded-full ${getStatusColor(props.status)}\`}\>  
             {props.status}  
           \</span\>  
         \</div\>  
         \<div className\="flex items-center text-sm text-muted-foreground"\>  
           \<User className\="h-4 w-4 mr-2" /\>  
           \<span\>Assigned to: {props.assignee}\</span\>  
         \</div\>  
         \<button   
           className\="mt-4 w-full bg-primary text-primary-foreground py-2 rounded-md hover:opacity-90"  
           onClick\={() \=\> callAction({ name: 'escalate\_ticket', payload: { title: props.title } })}  
         \>  
           Escalate  
         \</button\>  
       \</div\>  
     );  
   }

This combination of Python and JSX allows for the creation of arbitrarily complex and interactive UI elements tailored to any domain.

## **Part 6: Auditory Elements and Advanced Topics**

This final section addresses the remaining aspects of UI customization, including the specific meaning of "sound" in Chainlit, a synthesized guide to removing default branding, and an advanced communication method for embedded applications.

### **6.1. Clarifying "Sound" in Chainlit: The cl.Audio Element**

The request to customize how the UI "sounds" requires clarification. Based on the available documentation, Chainlit does not currently support the customization of UI event sounds, such as chimes for new messages or error notifications.

Instead, the framework's handling of "sound" pertains to the ability to display playable audio files *as content* within the chat interface. This is accomplished using the cl.Audio element.8 This element is for presenting audio information to the user, not for auditory feedback from the UI itself.

The cl.Audio element is configured with the following attributes:

* name: A string that serves as the display name for the audio file in the UI.  
* **Source (one of the following is required):**  
  * path: A string representing the local file path to an audio file.  
  * url: A string representing the remote URL of an audio file.  
  * content: The raw file content in bytes format.  
* display: Determines where the audio player is rendered. The options are "inline" (within the message flow), "side" (in the sidebar), or "page" (taking up the main content area). The default is "side".8  
* auto\_play: A boolean that, if true, will cause the audio to begin playing automatically as soon as it is rendered.

### **6.2. Removing Chainlit Branding: A Synthesis**

While there is no single hide\_branding \= true switch in Chainlit, it is possible to achieve a fully "white-labeled" application by systematically using the various customization features to replace every default branding element. This approach involves replacement, not simple removal.

Here is a comprehensive checklist for removing all default Chainlit branding:

1. **Set Application Name:** In config.toml, set the name parameter under the \[UI\] section to your application's name.9  
2. **Replace GitHub Link:** In config.toml, set the github parameter to your own repository's URL. This will replace the default link to the Chainlit GitHub repository.9  
3. **Replace Logo:** Add your custom logo\_dark.png and logo\_light.png files to the /public directory.2  
4. **Replace Favicon:** Add your custom favicon.png (or .ico) file to the /public directory.2  
5. **Customize Login Page:** If using authentication, set a custom login\_page\_image in config.toml to replace the default background, which features the Chainlit logo.2  
6. **Apply a Custom Theme:** Create a theme.json file to override all default colors and fonts, ensuring the application's look and feel is entirely your own.4

By following these steps, all user-facing default branding can be effectively replaced with custom assets and configurations.

### **6.3. Advanced Communication: Window Messaging for iFrames**

For advanced use cases where a Chainlit application is embedded within another website or application using an \<iframe\>, a special communication channel is needed. Chainlit provides a mechanism for this using standard browser window.postMessage APIs, allowing for bidirectional communication between the parent window and the embedded Chainlit app.17

#### **Parent Window to Chainlit App**

To send a message from the parent webpage *into* the Chainlit app, the parent's JavaScript can use postMessage on the iframe's content window.

* **Parent Window JavaScript:**  
  JavaScript  
  const iframe \= document.getElementById('chainlit-iframe');  
  iframe.contentWindow.postMessage('Client: Hello from parent window', '\*');

This message can be received and handled within the Chainlit Python code by using the @cl.on\_window\_message decorator.

* **Chainlit Python (app.py):**  
  Python  
  import chainlit as cl

  @cl.on\_window\_message  
  async def window\_message(message: str):  
      \# Process the message received from the parent window  
      if message.startswith("Client:"):  
          await cl.Message(content=f"Window message received: {message}").send()

#### **Chainlit App to Parent Window**

To send a message *from* the Chainlit app back out to the parent window, the cl.send\_window\_message() function is used in the Python code.

* **Chainlit Python (app.py):**  
  Python  
  import chainlit as cl

  @cl.on\_message  
  async def message():  
      await cl.send\_window\_message("Server: Hello from Chainlit")

The parent window can then listen for this message using a standard JavaScript event listener.

* **Parent Window JavaScript:**  
  JavaScript  
  window.addEventListener('message', (event) \=\> {  
    // It's good practice to check the origin for security  
    // if (event.origin\!== "http://your-chainlit-app-origin") return;

    if (typeof event.data \=== 'string' && event.data.startsWith("Server:")) {  
      console.log('Parent window received:', event.data);  
    }  
  });

This window messaging feature enables tight integration when Chainlit is used as a component within a larger web ecosystem.17

#### **Works cited**

1. Overview \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/backend/config/overview](https://docs.chainlit.io/backend/config/overview)  
2. Logo and Favicon \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/customisation/custom-logo-and-favicon](https://docs.chainlit.io/customisation/custom-logo-and-favicon)  
3. Avatars \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/customisation/avatars](https://docs.chainlit.io/customisation/avatars)  
4. Theme \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/customisation/theme](https://docs.chainlit.io/customisation/theme)  
5. CSS \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/customisation/custom-css](https://docs.chainlit.io/customisation/custom-css)  
6. JS \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/customisation/custom-js](https://docs.chainlit.io/customisation/custom-js)  
7. Custom \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/api-reference/elements/custom](https://docs.chainlit.io/api-reference/elements/custom)  
8. Audio \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/api-reference/elements/audio](https://docs.chainlit.io/api-reference/elements/audio)  
9. UI \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/backend/config/ui](https://docs.chainlit.io/backend/config/ui)  
10. Step \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/concepts/step](https://docs.chainlit.io/concepts/step)  
11. Migrate to Chainlit v1.1.300, accessed August 5, 2025, [https://docs.chainlit.io/guides/migration/1.1.300](https://docs.chainlit.io/guides/migration/1.1.300)  
12. Action \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/api-reference/action](https://docs.chainlit.io/api-reference/action)  
13. Action \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/concepts/action](https://docs.chainlit.io/concepts/action)  
14. Chat Profiles \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/advanced-features/chat-profiles](https://docs.chainlit.io/advanced-features/chat-profiles)  
15. Chat Profiles \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/api-reference/chat-profiles](https://docs.chainlit.io/api-reference/chat-profiles)  
16. Chat Settings \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/advanced-features/chat-settings](https://docs.chainlit.io/advanced-features/chat-settings)  
17. Web App \- Chainlit, accessed August 5, 2025, [https://docs.chainlit.io/deploy/webapp](https://docs.chainlit.io/deploy/webapp)