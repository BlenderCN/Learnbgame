float fract(float f)
{
return f - floor(f);
}

float smod(float val, float factor)
{
    float res = fmod(val,factor);
    if (res <0)
        res = factor+res;
    
    return res;
}

float _step(float low, float high, float value)
{
  float result;
  if (value < low) 
  {
    result = 0.0;
  }
    else 
        if (value >= high) result = 1.0;
    else {
        result = (value - low)/(high - low);
    } 
  return result;
}
