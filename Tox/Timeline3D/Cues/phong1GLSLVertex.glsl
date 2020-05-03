uniform vec4 uDiffuseColor;
uniform vec4 uAmbientColor;
uniform vec3 uSpecularColor;
uniform float uShininess;
uniform float uShadowStrength;
uniform vec3 uShadowColor;

out Vertex
{
	vec4 color;
	vec3 worldSpacePos;
	vec3 worldSpaceNorm;
	flat int cameraIndex;
} oVert;

in int index;

void main()
{

	vec3 newPosition = P;

	//newPosition.x += index;
	int instanceID = TDInstanceID();
	float fadeInStart = TDInstanceCustomAttrib0(instanceID).x;
	float fadeInEnd = TDInstanceCustomAttrib0(instanceID).y;
	float fadeOutStart = TDInstanceCustomAttrib0(instanceID).z;
	float fadeOutEnd = TDInstanceCustomAttrib0(instanceID).w;
	
	
	float cueHeight = TDInstanceCustomAttrib1(instanceID).x;
	float cueStartPos = cueHeight * .5;
	switch (index){
		case 0:
			newPosition.x = fadeInStart;
			newPosition.y = P.y - cueStartPos;
			break;
		case 1:
			newPosition.x = fadeInEnd;
			newPosition.y = P.y + cueHeight - cueStartPos*1.15;
			break;
		case 2:
			newPosition.x = fadeOutStart;
			newPosition.y = P.y + cueHeight - cueStartPos*1.15;

			break;
		case 3:
			newPosition.x = fadeOutEnd;
			newPosition.y = P.y - cueStartPos;

			break;

	}
	// First deform the vertex and normal
	// TDDeform always returns values in world space
	vec4 worldSpacePos = TDDeform(newPosition);
	vec3 uvUnwrapCoord = TDInstanceTexCoord(TDUVUnwrapCoord());
	gl_Position = TDWorldToProj(worldSpacePos, uvUnwrapCoord);


	// This is here to ensure we only execute lighting etc. code
	// when we need it. If picking is active we don't need lighting, so
	// this entire block of code will be ommited from the compile.
	// The TD_PICKING_ACTIVE define will be set automatically when
	// picking is active.
#ifndef TD_PICKING_ACTIVE

	int cameraIndex = TDCameraIndex();
	oVert.cameraIndex = cameraIndex;
	oVert.worldSpacePos.xyz = worldSpacePos.xyz;
	oVert.color = TDInstanceColor(Cd);
	vec3 worldSpaceNorm = normalize(TDDeformNorm(N));
	oVert.worldSpaceNorm.xyz = worldSpaceNorm;

#else // TD_PICKING_ACTIVE

	// This will automatically write out the nessessary values
	// for this shader to work with picking.
	// See the documentation if you want to write custom values for picking.
	TDWritePickingValues();

#endif // TD_PICKING_ACTIVE
}
