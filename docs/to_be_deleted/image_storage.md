# Image Storage for Webinar Registrants

This document explains the image storage structure and how to use fake people images in the application.

## 📁 Directory Structure

```
static/
├── uploads/
│   ├── photos/           # User-uploaded photos (UUID-based filenames)
│   └── sample_photos/    # Pre-loaded fake people images
└── images/               # Other static images (logos, etc.)
```

## 🖼️ Sample Photos

The application includes 5 sample professional headshots from Unsplash:

- `john_smith.jpg` - John Smith (Tech Corp)
- `sarah_johnson.jpg` - Sarah Johnson (Startup Inc)
- `michael_chen.jpg` - Michael Chen (Enterprise Solutions)
- `emily_davis.jpg` - Emily Davis (Freelance Developer)
- `david_wilson.jpg` - David Wilson (Tech Consulting)

## 🚀 Setup Instructions

### 1. Download Sample Photos
```bash
uv run python -m scripts.download_sample_photos
```

### 2. Add Registrants with Photos
```bash
uv run python -m scripts.clear_and_add_registrants
```

## 📝 How It Works

### **Sample Photos Storage**
- **Location**: `static/uploads/sample_photos/`
- **Purpose**: Source images for initialization
- **Format**: High-quality professional headshots
- **License**: Free to use (Unsplash)

### **User Photos Storage**
- **Location**: `static/uploads/photos/`
- **Naming**: UUID-based unique filenames
- **Purpose**: Actual user-uploaded photos
- **Security**: Prevents filename conflicts

### **Database Integration**
- **Field**: `photo_url` in `WebinarRegistrants` table
- **Format**: Relative path (e.g., `/static/uploads/photos/uuid_filename.jpg`)
- **Validation**: Only image files accepted
- **Size Limit**: 5MB per file

## 🔧 Scripts Available

### **Download Sample Photos**
```bash
uv run python -m scripts.download_sample_photos
```
- Downloads professional headshots from Unsplash
- Saves to `static/uploads/sample_photos/`
- Handles errors gracefully

### **Add Registrants with Photos**
```bash
uv run python -m scripts.add_sample_webinar_registrants
```
- Adds registrants without clearing existing ones
- Copies sample photos to user photos directory
- Generates unique filenames

### **Clear and Add Registrants**
```bash
uv run python -m scripts.clear_and_add_registrants
```
- Clears all existing registrants
- Adds fresh registrants with photos
- Perfect for demo resets

## 🎯 Usage Examples

### **For Development**
1. Run download script to get sample photos
2. Run clear_and_add script for fresh demo data
3. Access `/webinar-registrants` to see photos

### **For Production**
1. Replace sample photos with your own images
2. Update the initialization script with new filenames
3. Deploy with your custom images

### **Adding New Sample Photos**
1. Add new images to `static/uploads/sample_photos/`
2. Update the registrants list in the script
3. Run the initialization script

## 🔒 Security Considerations

- **File Validation**: Only image files accepted
- **Size Limits**: 5MB maximum per upload
- **Unique Names**: UUID-based filenames prevent conflicts
- **Path Security**: Files stored in controlled directory
- **Database Validation**: Photos only linked to existing registrants

## 📊 Database Schema

```sql
CREATE TABLE webinar_registrants (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    company VARCHAR,
    webinar_title VARCHAR NOT NULL,
    webinar_date TIMESTAMP NOT NULL,
    photo_url VARCHAR,  -- Path to uploaded photo
    -- ... other fields
);
```

## 🎨 Image Requirements

### **Recommended Specifications**
- **Format**: JPEG, PNG, GIF
- **Size**: 200x200px minimum (for thumbnails)
- **Quality**: High-resolution for professional look
- **Style**: Professional headshots preferred
- **License**: Ensure proper usage rights

### **File Naming Convention**
- **Sample Photos**: `firstname_lastname.jpg`
- **User Photos**: `uuid_originalname.ext`
- **Examples**: 
  - `john_smith.jpg` (sample)
  - `e3ff5a94-9dd8-4e0c-899a-e66d05493dc7_john_smith.jpg` (user)

## 🔄 Workflow

1. **Initial Setup**: Download sample photos
2. **Database Population**: Run initialization script
3. **User Uploads**: Photos stored with UUID names
4. **Display**: Photos served from static directory
5. **Management**: Delete photos via web interface

## 🛠️ Troubleshooting

### **Common Issues**
- **Missing Photos**: Run download script again
- **Permission Errors**: Check directory permissions
- **Database Errors**: Ensure migrations are applied
- **Display Issues**: Check file paths in database

### **Debug Commands**
```bash
# Check if photos exist
ls -la static/uploads/sample_photos/

# Check database records
uv run python -m scripts.check_users

# Test photo URLs
curl -I http://localhost:8000/static/uploads/photos/filename.jpg
```

This image storage system provides a complete solution for managing fake people images in the webinar registrants demo! 