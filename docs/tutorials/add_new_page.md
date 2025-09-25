# Add New Page

This guide covers adding new pages, testing, debugging, and best practices for the FastOpp application.

## Adding New Pages

### Overview

The Migration Guide page is a static documentation page that doesn't require any database models. It's purely a frontend page that displays information about how to use the existing migration system.

### Key Steps

1. Create a new template for the page
2. Add a route for the page
3. Update the header navigation
4. Add a card to the homepage

### Example: Adding Migration Guide Page

#### 1. Create Template

Create `templates/migration-guide.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Guide - FastOpp</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.7.2/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <div x-data="{ mobileMenuOpen: false }">
        <!-- Navigation content -->
    </div>

    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-green-600 to-green-800 text-white py-20">
        <div class="container mx-auto px-4 text-center">
            <h1 class="text-5xl font-bold mb-6">Migration Guide</h1>
            <p class="text-xl mb-8">Learn how to manage database migrations in your FastAPI application</p>
            <div class="flex justify-center space-x-4">
                <a href="#quick-start" class="bg-white text-green-800 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                    Quick Start
                </a>
                <a href="#commands" class="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-green-800 transition-colors">
                    Commands
                </a>
            </div>
        </div>
    </div>

    <!-- Content Sections -->
    <div class="container mx-auto px-4 py-16">
        <!-- Quick Start Section -->
        <section id="quick-start" class="mb-16">
            <h2 class="text-3xl font-bold text-gray-800 mb-8 text-center">Quick Start Guide</h2>
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- Step cards -->
            </div>
        </section>

        <!-- Commands Section -->
        <section id="commands" class="mb-16">
            <h2 class="text-3xl font-bold text-gray-800 mb-8 text-center">Migration Commands</h2>
            <!-- Command tables -->
        </section>
    </div>
</body>
</html>
```

#### 2. Add Route

Update `routes/pages.py`:

```python
@router.get("/migration-guide")
async def migration_guide(request: Request):
    """Migration Guide page"""
    return templates.TemplateResponse("migration-guide.html", {"request": request})
```

#### 3. Update Navigation

Update `templates/partials/header.html`:

```html
<nav class="hidden md:flex space-x-8">
    <a href="/" class="text-gray-300 hover:text-white transition-colors">Home</a>
    <a href="/migration-guide" class="text-gray-300 hover:text-white transition-colors">Migration Guide</a>
    <a href="/webinar-demo" class="text-gray-300 hover:text-white transition-colors">Webinar Demo</a>
    <!-- Other navigation items -->
</nav>
```

#### 4. Add Homepage Card

Update `templates/index.html`:

```html
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
    <!-- Existing cards -->
    
    <!-- Migration Guide Card -->
    <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
        <div class="flex items-center mb-4">
            <svg class="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <h3 class="text-xl font-semibold">Migration Guide</h3>
        </div>
        <p class="text-green-100 mb-4">Learn how to manage database migrations with Alembic in your FastAPI application.</p>
        <a href="/migration-guide" class="inline-block bg-white text-green-600 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Get Started
        </a>
    </div>
</div>
```
