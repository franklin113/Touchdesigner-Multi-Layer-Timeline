
uniform sampler2DArray sThumbnail;
uniform sampler2DArray sLabel;
uniform float uLineWidth;
uniform float uZoom;

in Vertex
{
	vec4 color;
	vec2 texCoord0;

	flat int instanceID;
	flat int selectionIndex;
	vec4 geoInfoText;
	vec4 geoInfoThumbnail;
	float aspect;

} iVert;



vec4 Over_Composite(vec4 top, vec4 bot){
	vec4 col = vec4(0);
	col.rgb = (top.rgb*top.a) + (bot.rgb*(1-top.a));
	col.a = (top.a) + (bot.a*(1-top.a));
	return col;
}


// float Outline(vec2 st, float width){

// 	float val = 0.0;

// 	if (st.x < width * uZoom || st.x > iVert.uvAspect - width * uZoom){
// 		val = 1.0;
// 	}
// 	if (st.y < width || st.y > 1.0 - width){
// 		val = 1.0;
// 	}

// 	return val;
	
// }

float Edge(vec2 uvs, float width){
	vec2 grid = abs(fract(uvs - 0.5) - 0.5) / fwidth(uvs)*width;
	float line = min(grid.x, grid.y);
	float edgeMask = 1.0 - min(line, 1.0);
	edgeMask = 1 - step( edgeMask , 0.6);
	return edgeMask;
}

// Output variable for the color
layout(location = 0) out vec4 oFragColor[1];
void main()
{
	// This allows things such as order independent transparency
	// and Dual-Paraboloid rendering to work properly
	TDCheckDiscard();
	int instanceID = iVert.instanceID;

	vec4 outcol = vec4(0.0, 0.0, 0.0, 0.0);

	// ----- LUCAS EXAMPLE

	TDCheckDiscard();
	vec4 color = iVert.color;
	
	// a nice way of getting the render top res in shader. best to use this if the shader is used on multiple renders.
	vec2 viewportRes = 1 / uTDGeneral.viewport.zw;

	// res of the top named sLabel. easier to get res dims this way than passing them in as extra uniforms.
	vec2 sLabelRes = vec2(textureSize(sLabel,0).xy);
	vec2 sThumbnailRes = vec2(textureSize(sThumbnail,0).xy);


	// XY position in 0:1 space of the geometry.
	vec2 XY = iVert.geoInfoText.xy;
	vec2 XY_Thumb = iVert.geoInfoThumbnail.xy;

	// screen space pixel uvs - just like vUV in a glsl TOP, but instead of normalized, 
	// in whole integer values in the range of the viewport rendering this shader.
	vec2 pixelUVs = gl_FragCoord.xy;

	// normalize the pixelUVS above into 0:1 space. only neccesary if we plan to use texture() instead of texelFetch()
	// texelFetch bypasses the automatic interpolation that texture() applies based on sampler settings.
	vec2 vUV = (pixelUVs / viewportRes);


	// offset the text UVS by the geo's 0:1 screen space position.
	// NOTE: At this point, the text is still distorted, but tracks with bottom left of geo.
	vec2 textUVs = vUV-XY;
	vec2 thumbnailUVs = vUV-XY_Thumb;

	// fix the distortion of the uvs, making the text render at 1:1 native res.
	// since our uv's originate not from our geometry, but from our screen, we do not need to take into account
	// the maths of the surface UVS. we have no used those in any way so far.
	
	float thumbnailHeight = (iVert.geoInfoThumbnail.w * iVert.geoInfoThumbnail.y);
	float thumbnailWidth = (iVert.geoInfoThumbnail.z - iVert.geoInfoThumbnail.x);
	
	float geoAspect = thumbnailWidth / thumbnailHeight;

	vec2 uv = iVert.texCoord0;


	textUVs /= ( sLabelRes / viewportRes );
	// thumbnailUVs /= ( sThumbnailRes / viewportRes) * thumbnailHeight * 1.5;
	thumbnailUVs = uv;
	thumbnailUVs.x /= iVert.aspect;
	thumbnailUVs.x /= uZoom;
	// sample the label.
	vec4 thumbnail = texture( sThumbnail , vec3(thumbnailUVs,uInstanceMap[instanceID] ));
	vec4 label = texture( sLabel , vec3(textUVs,uInstanceMap[instanceID] ));
	
	// over composite the label.
	color = Over_Composite( thumbnail , color );
	color = Over_Composite( label , color );
	vec3 selectionColors[3] = vec3[](vec3(0.1843, 0.1843, 0.1843),vec3(1.0,1.0,1.0),vec3(1.0, 0.9882, 0.3882));

	
	// 
	if (iVert.selectionIndex > 0 ){
		float edgeMask = Edge(uv * 1 , uLineWidth);
		
		color.rgb += selectionColors[iVert.selectionIndex] * edgeMask;
	}
	outcol = color;
	// --- END LUCAS EXAMPLE

	float alpha = 1.;


	// Dithering, does nothing if dithering is disabled
	outcol = TDDither(outcol);

	outcol.rgb *= alpha;
	// Modern GL removed the implicit alpha test, so we need to apply
	// it manually here. This function does nothing if alpha test is disabled.
	TDAlphaTest(alpha);

	outcol.a = alpha;

	oFragColor[0] = TDOutputSwizzle(outcol);

}
