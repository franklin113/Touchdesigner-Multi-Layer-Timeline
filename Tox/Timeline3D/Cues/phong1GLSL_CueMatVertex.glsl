
uniform float uZoom, uLineWidth;
out Vertex
{
	vec4 color;
	vec2 texCoord0;
	flat int instanceID;
	flat int selectionIndex;
	vec4 geoInfoText;
	float aspect;
} oVert;


// the map functions just make life a little bit easier.
vec2 Map( vec2 value, vec2 min1, vec2 max1, vec2 min2, vec2 max2 ){
	vec2 perc = (value - min1) / (max1 - min1);
	return perc * (max2 - min2) + min2;
}

void main()
{

	{ // Avoid duplicate variable defs
		vec3 texcoord = TDInstanceTexCoord(uv[0]);
		oVert.texCoord0.st = texcoord.st;
	}
	int instanceID = TDInstanceID();

	vec4 GeoInfo = TDInstanceCustomAttrib2(instanceID);
	// Begin Lucas Morgan's Assistance Code

	// a nice way of getting the render top res in shader. best to use this if the shader is used on multiple renders.
	vec2 viewportRes = 1 / uTDGeneral.viewport.zw;
	// create two coordinates, one for Left/Bottom and one for Right/Top:
	// this holds all the info we will need about our geometry.
	// If we were dealing with geo instances, we could get this from TDInstanceCustomAttrib0(); instead of a uniform.
	
	vec2 offsets = vec2(0,0);

	oVert.aspect = GeoInfo.w / GeoInfo.z;

	float bottom = GeoInfo.y - GeoInfo.w * .5 ;
	//GeoInfo.y + offsets[1]
	vec4 LB_Text = vec4( GeoInfo.x + offsets[0] , bottom + offsets[1], 0 , 1 );
	vec4 RT_Text = vec4( GeoInfo.x+ offsets[0] + GeoInfo.z , GeoInfo.y+GeoInfo.w + bottom + offsets[1], 0 , 1 );


	// points are converted to projection space, then remapped from that to 0:1 space.
	vec2 LB_2d_Text = Map( TDWorldToProj( LB_Text ).xy, vec2(-1.0) , vec2(1.0) , vec2(0) , vec2(1) ); // viewportRes.xy 
	vec2 RT_2d_Text = Map( TDWorldToProj( RT_Text ).xy, vec2(-1.0) , vec2(1.0) , vec2(0) , vec2(1) );

	// LEFT STOP - this important bit causes the left edge of the text to clamp to the left edge of the screen.
	// since the geo position is conveniently in 0-1 space, 0 being the bottom/left edge of the screen - we can just clamp at 0.
	// NOTE: we're not using RT_2d.x in the fragment shader, but if we were - we'd want to treat it the same way as the left edge.
	
	LB_2d_Text += .01;
	LB_2d_Text.x = max( LB_2d_Text.x, 0.005 ); // left side
	RT_2d_Text.x = max( RT_2d_Text.x, 0.005 ); // right side

	// put the relevant values into a vec4, and send this to the fragment shader.
	oVert.geoInfoText = vec4( LB_2d_Text , RT_2d_Text );
	// oVert.geoInfoThumbnail = vec4( LB_2d_Thumb , RT_2d_Thumb );

	// End Lucas Morgan's example code 




	oVert.instanceID = instanceID;

	oVert.selectionIndex = min(2,int(TDInstanceCustomAttrib1(instanceID).x)+1);


	// vec3 uvUnwrapCoord = TDInstanceTexCoord(TDUVUnwrapCoord());
	vec4 worldSpacePos = TDDeform(P);
	
	gl_Position = TDWorldToProj(worldSpacePos);


#ifndef TD_PICKING_ACTIVE

	oVert.color = TDInstanceColor(Cd);

	int cameraIndex = TDCameraIndex();



#else // TD_PICKING_ACTIVE

	TDWritePickingValues();

#endif // TD_PICKING_ACTIVE
}
