# Risk Buffer Radius Analysis

## Summary

**Decision**: Maintain 1km radius for risk buffer zones around fire hotspots.

**Reasoning**: While NASA VIIRS data has a 375m sensor resolution, a 1km buffer provides optimal safety margin for wildfire early-warning systems.

## Technical Analysis

### NASA VIIRS Data Specifications
- **Sensor Resolution**: 375m
- **Imagery Resolution**: 250m  
- **Thermal Anomaly Representation**: Red points at approximate center of 375m pixels
- **Temporal Resolution**: Twice daily observations
- **Spatial Accuracy**: Improved mapping of large fire perimeters and small area fires

### Risk Buffer Considerations

#### Why 375m Would Be Technically Accurate
- Matches the actual VIIRS sensor pixel size
- Represents the precise area of fire detection
- Aligns with NASA's data resolution specifications

#### Why 1km Provides Better Operational Value
1. **Safety Margin**: Fire spread can extend beyond immediate detection pixels
2. **Emergency Planning**: Provides adequate buffer for evacuation planning
3. **Real-world Conditions**: Accounts for wind, terrain, and fire behavior variations
4. **Early Warning System**: Conservative approach ensures public safety
5. **Response Time**: Gives emergency services sufficient notice and area coverage

## Implementation

The risk buffer is implemented as:
- **Radius**: 1,000 meters (1km)
- **Visual Style**: Red translucent circles around each hotspot
- **Interactive**: Toggleable via legend controls
- **Real-time**: Updates with new fire data

## Conclusion

While 375m represents the technical accuracy of NASA's VIIRS data, the 1km risk buffer radius provides the optimal balance between scientific precision and operational safety for wildfire early-warning systems. This conservative approach ensures maximum protection for communities while maintaining the system's scientific foundation.

---

*This analysis is based on NASA FIRMS VIIRS data specifications and wildfire management best practices.* 