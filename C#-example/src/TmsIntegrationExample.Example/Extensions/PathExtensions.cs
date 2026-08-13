// <copyright file="PathExtensions.cs" company="Engaged Technologies">
//     Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//    PathExtensions class
// </summary>

using System.IO;
using System.Reflection;

namespace TmsIntegrationExample.Example.Extensions
{
    public static class PathExtensions
    {
        public static string PathFromExecutingAssemblyLocation(this string path)
        {
            return Path.Combine(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location), path);
        }
    }
}
