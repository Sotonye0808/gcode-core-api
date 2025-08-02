# GCode Core API Documentation

## Overview

The GCode Core API is a RESTful web service that provides SVG to G-code conversion, user data management, and secure data storage capabilities. Built with Django REST Framework, it offers robust endpoints for data persistence and signed request handling from trusted frontend applications.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API provides two types of access:

### 1. Open Access

Standard API endpoints that accept requests from any host and return their output without authentication.

### 2. Signed Requests

Special endpoints that only accept requests from trusted frontend origins with HMAC signature verification. These endpoints can store and modify database records.

## Response Format

All API responses follow a consistent JSON format:

### Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully"
}
```

### Error Response

```json
{
  "success": false,
  "details": "Detailed error message"
}
```

## Rate Limiting

- **Rate Limit**: 100 requests per hour per IP address
- **Headers**: Rate limit information is included in response headers

## Open Access Endpoints

These endpoints accept requests from any host and do not require authentication.

### 1. Health Check

**GET** `/health/`

Check API service status and get endpoint information.

**Response:**

```json
{
  "status": "healthy",
  "service": "GCode Core API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "endpoints": {
    "convert": "/api/convert/",
    "signed_submit": "/api/signed/submit/",
    "signed_retrieve": "/api/signed/retrieve/"
  }
}
```

---

### 2. SVG to G-code Conversion

**POST** `/convert/`

Convert SVG data to G-code for CNC machines or 3D printers.

**Content-Type:** `application/json` OR `multipart/form-data`

#### Request Options

##### Option 1: Raw SVG Data (JSON)

```json
{
  "svg_data": "<svg width=\"100\" height=\"100\" xmlns=\"http://www.w3.org/2000/svg\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\" fill=\"none\" stroke=\"black\"/></svg>"
}
```

##### Option 2: File Upload (Form Data)

```
Content-Type: multipart/form-data
svg_file: [file.svg]
```

#### Response

```json
{
  "success": true,
  "gcode": "G28\nG1 Z0.0\nM05\nG0 X10.0 Y90.0\nM03\nG1 X90.0 Y90.0\n...",
  "message": "SVG converted successfully to G-code",
  "metadata": {
    "gcode_lines": 150,
    "gcode_size": 2048,
    "movement_commands": 120,
    "setup_commands": 30,
    "estimated_duration": "15.0 seconds"
  }
}
```

#### Error Responses

- **400 Bad Request**: Invalid SVG data or format
- **413 Payload Too Large**: File size exceeds limit (10MB)
- **500 Internal Server Error**: Conversion processing error

---

## Signed Request Endpoints

These endpoints require HMAC signature verification from trusted frontend origins.

### Required Headers

- **Origin**: Must be from a trusted frontend origin
- **Content-Type**: `application/json`

### Signature Generation

Requests must include a `request_signature` field with an HMAC-SHA256 signature of the request data.

#### Signature Algorithm:

1. Remove `request_signature` field from request data
2. Sort remaining fields alphabetically by key
3. Create canonical string: `key1=value1&key2=value2&...`
4. Generate HMAC-SHA256 using the frontend signing key
5. Include the hex digest as `request_signature`

### 1. Submit User Data and Signature

**POST** `/signed/submit/`

Submit user information and SVG signature data for storage.

#### Request Format

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "student",
  "department": "Computer Science",
  "faculty": "Engineering",
  "svg_data": "<svg width=\"200\" height=\"100\"><path d=\"M10,50 Q50,10 90,50 T170,50\" stroke=\"black\" fill=\"none\"/></svg>",
  "request_signature": "a1b2c3d4e5f6789..."
}
```

#### Request Fields

| Field               | Type   | Required | Description                      |
| ------------------- | ------ | -------- | -------------------------------- |
| `name`              | string | Yes      | User's full name (max 255 chars) |
| `email`             | string | Yes      | User's email address (unique)    |
| `role`              | string | No       | User role (default: "student")   |
| `department`        | string | No       | User's department                |
| `faculty`           | string | No       | User's faculty                   |
| `svg_data`          | string | Yes      | SVG signature content            |
| `request_signature` | string | Yes      | HMAC signature                   |

#### Role Options

- `student` (default)
- `lecturer`
- `hod` (Head of Department)
- `dean`
- `researcher`
- `visitor`
- `other`

#### Response

```json
{
  "success": true,
  "message": "Data submitted successfully",
  "user_id": 123,
  "signature_id": 456
}
```

#### Error Responses

- **400 Bad Request**: Invalid data or validation errors
- **403 Forbidden**: Invalid signature or untrusted origin
- **500 Internal Server Error**: Database or conversion error

---

### 2. Retrieve User Data

**POST** `/signed/retrieve/`

Retrieve all stored data for a user by email address.

#### Request Format

```json
{
  "email": "john@example.com",
  "request_signature": "a1b2c3d4e5f6789..."
}
```

#### Response

```json
{
  "success": true,
  "user": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student",
    "department": "Computer Science",
    "faculty": "Engineering",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:30:00Z",
    "submitted_at": "2024-01-01T10:00:00Z"
  },
  "signatures": [
    {
      "id": 456,
      "svg_data": "<svg>...</svg>",
      "gcode_data": "G28\nG1 X0 Y0\n...",
      "metadata": {
        "gcode_lines": 25,
        "gcode_size": 512,
        "movement_commands": 20,
        "setup_commands": 5,
        "estimated_duration": "2.5 seconds"
      },
      "created_at": "2024-01-01T10:15:00Z"
    }
  ]
}
```

#### Error Responses

- **400 Bad Request**: Invalid email format
- **403 Forbidden**: Invalid signature or untrusted origin
- **404 Not Found**: User not found
- **500 Internal Server Error**: Database error

---

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error Type",
  "details": "Detailed error message"
}
```

### Common Error Types

- **Validation error**: Invalid input data
- **Authentication error**: Invalid or missing signature
- **Permission denied**: Untrusted origin
- **Not found**: Resource not found
- **Internal server error**: Unexpected server error

### HTTP Status Codes

| Code | Meaning                              |
| ---- | ------------------------------------ |
| 200  | Success                              |
| 400  | Bad Request - Invalid input          |
| 403  | Forbidden - Authentication failed    |
| 404  | Not Found - Resource not found       |
| 413  | Payload Too Large - File too big     |
| 500  | Internal Server Error - Server error |

---

## Integration Examples

### Frontend Integration (JavaScript)

```javascript
// HMAC signature generation
function generateSignature(data, signingKey) {
  const canonicalString = createCanonicalString(data);
  return CryptoJS.HmacSHA256(canonicalString, signingKey).toString();
}

function createCanonicalString(data) {
  const cleanData = { ...data };
  delete cleanData.request_signature;

  const sortedKeys = Object.keys(cleanData).sort();
  const parts = sortedKeys.map((key) => {
    let value = cleanData[key];
    if (typeof value === "object") {
      value = JSON.stringify(value);
    } else if (value === null || value === undefined) {
      value = "";
    }
    return `${key}=${value}`;
  });

  return parts.join("&");
}

// Submit user data
async function submitUserData(userData) {
  const requestData = {
    ...userData,
    request_signature: generateSignature(userData, SIGNING_KEY),
  };

  const response = await fetch("/api/signed/submit/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: window.location.origin,
    },
    body: JSON.stringify(requestData),
  });

  return response.json();
}
```

---

## Testing

### Health Check Test

```bash
curl -X GET http://localhost:8000/api/health/
```

### SVG Conversion Test

```bash
curl -X POST http://localhost:8000/api/convert/ \
  -H "Content-Type: application/json" \
  -d '{
    "svg_data": "<svg width=\"100\" height=\"100\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\"/></svg>"
  }'
```

### Signed Request Test (requires valid signature)

```bash
curl -X POST http://localhost:8000/api/signed/submit/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "svg_data": "<svg><rect x=\"0\" y=\"0\" width=\"50\" height=\"50\"/></svg>",
    "request_signature": "valid_hmac_signature_here"
  }'
```

---

## Configuration

### Trusted Origins

Configure trusted frontend origins in environment variables:

```env
TRUSTED_FRONTEND_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Signing Key

Set a secure signing key for HMAC verification:

```env
FRONTEND_SIGNING_KEY=your-secure-signing-key-here
```

### CORS Settings

Configure CORS for frontend integration:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Database Models

### User Model Fields

| Field          | Type        | Description                    |
| -------------- | ----------- | ------------------------------ |
| `id`           | Integer     | Primary key (auto-generated)   |
| `name`         | String(255) | User's full name               |
| `email`        | Email       | Unique email address           |
| `role`         | Choice      | User's role (default: student) |
| `department`   | String(255) | Department (optional)          |
| `faculty`      | String(255) | Faculty (optional)             |
| `created_at`   | DateTime    | Record creation time           |
| `updated_at`   | DateTime    | Last update time               |
| `submitted_at` | DateTime    | First submission time          |

### SignatureData Model Fields

| Field            | Type       | Description                  |
| ---------------- | ---------- | ---------------------------- |
| `id`             | Integer    | Primary key (auto-generated) |
| `user`           | ForeignKey | Reference to User model      |
| `svg_data`       | Text       | SVG content                  |
| `gcode_data`     | Text       | Generated G-code             |
| `gcode_metadata` | JSON       | G-code statistics            |
| `created_at`     | DateTime   | Record creation time         |

---

## Performance Considerations

### Database Optimization

- Indexed email field for fast user lookups
- Efficient foreign key relationships
- JSON metadata for flexible G-code statistics

### File Handling

- Temporary file cleanup for SVG processing
- Memory-efficient file upload handling
- Configurable file size limits

### Security

- HMAC signature verification for trusted requests
- Origin validation for signed endpoints
- Input validation and sanitization
- CORS configuration for frontend integration

---

## Support

For technical support or questions about the Core API:

1. Check this documentation
2. Review the README.md file
3. Check Django logs in the `logs/` directory
4. Run the test suite to verify functionality

**Author**: Sotonye Dagogo  
**Email**: sotydagz@gmail.com  
**GitHub**: [@Sotonye0808](https://github.com/Sotonye0808)
