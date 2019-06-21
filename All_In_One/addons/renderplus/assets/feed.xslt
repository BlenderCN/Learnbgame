<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> 
<xsl:template match="/">
<html>
<head>
    <title><xsl:value-of select="rss/channel/title"/></title>
    <link rel="stylesheet" type="text/css" href="feed.css"/>
</head>
<body>
<h1><xsl:value-of select="rss/channel/title"/></h1>
    <p id="description"><xsl:value-of select="rss/channel/description"/></p>

<h2>Progress</h2>
<div id="progress">
    <p><xsl:value-of select="rss/channel/item[1]/description"/></p>
    <p id="last_update">
        <h3>Last update</h3>
        <xsl:value-of select="rss/channel/lastBuildDate"/>
    </p>
</div>
    
<h2>Render jobs</h2>
<xsl:for-each select="rss/channel/item">
    <xsl:if test="title != 'Progress'">
        <article>
            <xsl:if test="contains(title, 'FINISHED')">
                <h3 class="status_finished">
                    <xsl:value-of select="title"/>
                </h3>
            </xsl:if>
            
            <xsl:if test="contains(title, 'DISABLED')">
                <h3 class="status_disabled">
                    <xsl:value-of select="title"/>
                </h3>
            </xsl:if>
            
            <xsl:if test="contains(title, 'FAILED')">
                <h3 class="status_disabled">
                    <xsl:value-of select="title"/>
                </h3>
            </xsl:if>
                    
            <h4>Settings</h4>
            <p><xsl:value-of select="description"/></p>
        </article>
    </xsl:if>
</xsl:for-each>

</body>
</html>

</xsl:template>
</xsl:stylesheet> 
