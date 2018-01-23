# Poster Specification

Poster spec is a file that describes parameters of a poster, namely placement and dimensions 
of various poster elements, thus serves as sort of a template for poster creation.

## Files Location

Management command for loading the specs into the database (`manage.py load_specs`)
expects the files to reside in `src/specs` directory. All files in there are read and parsed.

## File Format

Spec file is a JSON dictionary with following keys:

* __name__ (a descriptive name)
* __w__ (width of the poster in mm)
* __h__ (height of the poster in mm)
* __color__ (color value, as a HEX triplet, serving to visually distinguish different specs in the frontend app)
* __thumb__ (base64-encoded thumbnail of how the final poster may look like)
* __frames__ (dictionary of elements and their visual parameters, such as placement, dimensions, or color)
* __static_fields__ (dictionary of non-editable elements and their content, such as base64-encoded image data)
* __editable_fields__ (dictionary of elements that are supposed to be populated with content)

### `frames`

`frames` key holds a dictionary of all elements of the page. Text frame has following form:

```javascript
{
  "text_frame_id_string": {
    "x": 12,             // Horizontal position in mm (mandatory).
    "y": 12,             // Vertical position in mm (mandatory).
    "w": 100,            // Frame width in mm (optional). When specified, text is rendered within the frame bounds. 
    "h": 200,            // Frame height in mm (optional/mandatory when width is specified).
    "font_size": 36,     // Font size (optional) in typographical points. Default is 16.
    "color": "#c4151c",  // Text color (optional). CSS-like HEX triplet, default is "#000000".
    "align": "center"    // Text alignment (optional). Possible values are "center", "left", "right", default is "left",   
  }
}
```

Whereas image frame looks like this:

```javascript
{
  "image_frame_id_string": {
    "x": 12,   // Horizontal position in mm (mandatory).
    "y": 12,   // Vertical position in mm (mandatory).
    "w": 100,  // Frame width in mm (optional). When specified, image is scaled into the frame, preserving aspect ratio.  
    "h": 200   // Frame height in mm (optional/mandatory when width is specified).
  }
}
```

Each ID string must also be present in either `static_fields` or `dynamic_fields` 

### `static_fields`

`static_fields` key holds a dictionary of those elements of the page, that stay the same for each poster.

```javascript
{
  "text_frame_id_string": {
    "type": "text",                // Type of the field (mandatory).
    "name": "a descriptive name",  // Field name (optional).
    "text": "some text"            // The text to be rendered (mandatory).
  }
}
```

```javascript
{
  "image_frame_id_string": {
    "type": "image",              // Type of the field (mandatory).
    "name": "a descriptive name", // Field name (optional).
    "filename": "image.png",      // File name (mandatory). Used when storing the file.
    "data": "somedata"            // Base64-encoded image data. Allowed formats are JPEG and PNG.
  }
}
```

### `dynamic_fields`

`dynamic_fields` key holds a dictionary of those elements to be populated through API.

```javascript
{
  "text_frame_id_string": {
    "type": "text",                // Type of the field (mandatory).
    "name": "a descriptive name",  // Field name (mandatory). The name is important for frontend UI. 
    "char_limit": 20,              // Character limit (optional). Used by frontend UI.
    "mandatory": true              // If the field must be filled. Default is false.
  }
}
```

`text` value is to be added by frontend and saved with poster instance.

```javascript
{
  "image_frame_id_string": {
    "type": "image",           // Type of the field (mandatory).
    "name": "Hlavní obrázek",  // Field name (mandatory). Used by frontend UI.
    "width": 100,              // Image width (optional). Used by frontend UI for prescaling.
    "height": 200,             // Image height (optional/mandatory when width is specified).
    "mandatory": true          // If the field must be filled. Default is false.
  }
}
```

`filename` and `data` values are to be added by frontend and saved with poster instance.
