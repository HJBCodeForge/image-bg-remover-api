# Memory Optimization Fix for 512MB Limit

## Problem
The deployment was failing with:
```
Ran out of memory (used over 512MB) while running your code.
```

This was happening because:
1. **Eager Loading**: The rembg model was being loaded immediately at startup
2. **Large Models**: The u2net model consumes significant memory
3. **No Memory Optimization**: Large images were processed without resizing

## Solution Applied

### 1. Lazy Loading Implementation
- **Background Remover**: Changed from eager initialization to lazy loading
- **ML Model**: The rembg session is only created when first needed
- **Memory Savings**: App starts with minimal memory footprint

### 2. Model Selection Optimization
- **Priority Order**: u2net_lite → silueta → u2net → no session
- **u2net_lite**: Most memory-efficient model
- **silueta**: Alternative lightweight model
- **Fallback**: Graceful degradation if session creation fails

### 3. Image Processing Optimization
- **Reduced Max Size**: 800px (was 1024px) to save memory
- **Format Conversion**: Force RGB conversion for consistency
- **Aggressive Cleanup**: Close all image objects and buffers immediately
- **Garbage Collection**: Force GC after each operation

### 4. Runtime Optimization
- **Single Worker**: `--workers 1` to limit memory usage
- **Python Optimization**: `PYTHONOPTIMIZE=1` for bytecode optimization
- **Memory Trim**: `MALLOC_TRIM_THRESHOLD_=65536` for better memory management

### 5. Lazy Initialization Pattern
```python
# Before: Eager loading at startup
bg_remover = BackgroundRemover()  # Loaded immediately

# After: Lazy loading on first use
bg_remover = None
def get_background_remover():
    global bg_remover
    if bg_remover is None:
        bg_remover = BackgroundRemover()
    return bg_remover
```

### 6. Memory Monitoring
- **Health Endpoint**: Shows current memory usage
- **Memory Tracking**: Monitor RSS and percentage
- **Debugging**: Easy to identify memory spikes

## Technical Details

### Memory Usage Breakdown
- **Base FastAPI**: ~20-30MB
- **rembg Library**: ~50-80MB (when loaded)
- **u2net_lite Model**: ~100-150MB (vs 200-300MB for u2net)
- **Image Processing**: ~10-50MB per request (depends on image size)

### Memory Timeline
1. **Startup**: ~30MB (no model loaded)
2. **First Request**: ~180MB (model loads)
3. **Processing**: ~200-250MB (temporary spikes)
4. **Idle**: ~180MB (model cached)

### File Size Limits
- **Maximum Upload**: 5MB (already implemented)
- **Maximum Processing**: 800px max dimension
- **Output Optimization**: PNG with optimize=True

## Expected Results
- **Startup Memory**: Under 100MB
- **Processing Memory**: Under 400MB
- **Idle Memory**: Under 200MB
- **Memory Efficiency**: 40-60% improvement

## Monitoring
Use the health endpoint to monitor memory usage:
```bash
curl https://bg-remover-api-052i.onrender.com/health
```

## Fallback Strategy
If memory issues persist:
1. Use even smaller models (silueta only)
2. Reduce image size limit further (600px)
3. Implement request queuing to prevent concurrent processing
4. Use background tasks for processing
