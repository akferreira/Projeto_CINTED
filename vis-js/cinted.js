function teste(){
    console.log("aaaaaaaaaaa cinted");
}

function insert_node(id, label,group,hide,xcord, ycord, courseid = null,module = null){
console.log(`${hide} hide`);
    if(hide === undefined){
        hide = false;
    }
    
    var fixedY = true;
    
    if(ycord === null){
        fixedY = false;
    }
    var border_color = ["#ff0000","#171796","#ae624c","#50494a","#065535","#833f4d","#ff9900","#318ce7","#cd7f32","#a67b5b"];
    
    try{
       
        node_info.add({id : id, label: label, group: group,courseid : courseid, y: ycord,borderWidth: 2, color : {border: border_color[module]}, x: xcord,fixed: {
     x: true,
     y: fixedY,
   }
});
         //console.log(`node ${id} inserted! ${hide}`);
    }
  
    catch(e){
    
            if(group === "Resources") node_info.update([{id : id, hidden: hide}]);
        
    
           //console.log(`resources ${group === "Resources"} ${group}`);
    }
}

function insert_edge(idA,idB,count,log10_timedelta,hide,timedeltas){
    if(hide === undefined){
        hide = false;
    }

     try{
     var rlabel;
     var title;
     
     if(!(timedeltas === undefined)){
        title = timedeltas.toString();
     }
     
     
     if(count <= 1){
        count = 1;
        rlabel = 0;
     }
     else{
        rlabel = `<b>${count}</b>`
     }
     
    if(count > 8){
        count = 8 + count/10;
    } 
     
     
    r_info.add({from: idA, to: idB,width: count,font: { multi: true },title : title,label:rlabel,smooth: {type: 'curvedCW', roundness: 0.3*toggle}});
    //,smooth: {type: 'curvedCW', roundness: 0.3*toggle}
    //r_info.add({from: idA, to: idB,width: count,length: 100 + 1*log10_timedelta});
    toggle *= -1;
  }
  
  catch(e){
  
    r_info.update([{id : id, hidden: hide}]);
    network.redraw();
  }
}

function getEdgeBetweenNodes(node1,node2) {
    edges =  r_info.get().filter(function (edge) {
        return (edge.from === node1 && edge.to === node2 ) //|| (edge.from === node2 && edge.to === node1)
    });
    
    return edges.length > 0;
    
};

function average_delta(){}

function create_graph_access_order(result, hide,courseid){
        const singleRecord = result.records[0];
        const node = singleRecord.get(0);
        
        if(hide === undefined){
        hide = false;
        }
        
        var hideA;
        var hideB = hide;
        var xcord = null;
        var index = 0;
        var ycord = 30;
        var increment_y = 180;
        
        var ycord_map = new Map;
        
//         console.log(`${hide} hide`);

        for (record of result.records){
            idA = record.get("id(A)").toNumber();
            idB = record.get("id(B)").toNumber();
            index+=2;
        
            var nameA;
            var xb;

            if(record.get('typeA') == "Student"){
                nameA =  record.get('A').properties.trajectory_name;
                hideA = false;
            }
            
            else if(record.get('typeA') == "Courses"){
                nameA =  record.get('A').properties.coursename;
                hideA = false;
                if(xcord === null){
                xcord = mapCoursePosition.get(idA);
                 xb = mapCoursePosition.get(idB);
                }
                console.log(`${xcord} || ${xb}`);
                 console.log(`${idA} . ${idB}`);
            
            }
            else{
                nameA = record.get('A').properties.name;
                hideA = hide;
                
            }
           
           
            


            


            
            nameB = record.get('B').properties.name;

            
            
            

            const count = record.get('r').properties.count.toNumber();
            var groupA = record.get('typeA')[0];
            var groupB = record.get('typeB')[0];

            
            timedeltas = record.get('r').properties.timedeltas;
            var total = 0;

            for (timedelta of timedeltas){
            total += parseInt(timedelta,10);
            }

            average = total/timedeltas.length;

          //  console.log(average);
            timeformatted = new Date(average * 1000)

            log10_timedelta = Math.log10(average+1);

           // console.log(Math.log10(average+1));
           
            console.log(`ycord order ${ycord} ${idA}/${nameA} ${idB}/${nameB} : ${ycord} ${increment_y}`);
        
            var already_added = ycord_map.has(idA);
            
            insert_node(idA,nameA,groupA,hideA,xcord,ycord);
            if(!ycord_map.has(idA)) ycord += increment_y;
            insert_node(idB,nameB,groupB,hideB,xcord, ycord);
             if(!ycord_map.has(idB)) ycord += increment_y;
//             if(hideB == true) insert_node(idB,nameB,groupB,true);
//             else insert_node(idB,nameB,groupB,false);
            
           ycord_map.set(idA, true);
           ycord_map.set(idB, true);
            
            if(getEdgeBetweenNodes(idA,idB) == false){
                insert_edge(idA,idB,count,log10_timedelta,hide,timedeltas);
                }
            //console.log(getEdgeBetweenNodes(idA,idB));
            
        
        }


}

function create_graph_course_order(result){
   var course_count = 0;

    for (record of result.records){
            var nameA;

            if(record.get('typeA') == "Student"){
                nameA =  record.get('A').properties.trajectory_name;
                console.log(`${record.get("id(A)").toNumber()} ....`);
            }
            
            else if(record.get('typeA') == "Courses"){
                nameA =  record.get('A').properties.coursename;
                

            
            }

            else{
                nameA = record.get('A').properties.name;
            }


            
            nameB = record.get('B').properties.name;
            courseB = Number(record.get('B').properties.courseid)
            moduleB = record.get('B').properties.module;
            
            relation = record.get('r')
            idA = record.get("id(A)").toNumber();
            idB = record.get("id(B)").toNumber();
             console.log(`${idA} . ${idB}`);
            console.log();
            
            
            var xcord = course_count*250;
            if(course_count == 0) xcord-=100;
            
            if(mapCoursePosition.has(idA) == false) mapCoursePosition.set(idA, xcord);
            course_count+=1;
            
            
             if(course_count > 22) course_count+=1;
            var xcord2 = course_count*250;
           
            
            if(mapCoursePosition.has(idB) == false) mapCoursePosition.set(idB, xcord2);
             course_count+=1;
             console.log(`xcord course ${xcord}`);
            
            var groupA = record.get('typeA')[0];
            var groupB = record.get('typeB')[0];
        
            insert_node(idA,nameA,groupA,false,xcord,-100);
            insert_node(idB,nameB,groupB,false,xcord2,-100,courseB,moduleB);
            insert_node(relation.identity.toNumber(), `Curso id ${courseB}\nNota ${relation.properties.grade}\nModulo ${moduleB}`,"Resources",false,xcord2, -200);
            insert_edge(idA,idB,0,1);
            
            
            
        
        }



}
